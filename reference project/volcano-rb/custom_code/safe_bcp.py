"""
Safe BCP client socket that handles the case where the connection to
the display was never established (required: false). Workaround for
MPF 0.80.0.dev7 bugs:
  1. Receive loop starts with _receiver=None -> AttributeError
  2. bcp_interface.bcp_reset() waits for reset_complete from all named
     clients; a non-connected client never sends it, deadlocking the
     machine_reset_phase_1 queue indefinitely.
"""
import asyncio
from mpf.core.bcp.bcp_socket_client import BCPClientSocket


class SafeBCPClientSocket(BCPClientSocket):
    """Subclass of BCPClientSocket that guards against a None connection."""

    async def read_message(self):
        if self._receiver is None:
            # Connection was never established; cancel the receive loop cleanly.
            raise asyncio.CancelledError()
        return await super().read_message()

    def send(self, bcp_command, kwargs):
        if self._sender is None:
            # Not connected — drop the message, but if it's "reset" we must
            # immediately ack reset_complete so machine_reset_phase_1 can proceed.
            if bcp_command == "reset":
                asyncio.ensure_future(
                    self.machine.bcp.interface.bcp_receive_commands["reset_complete"](
                        client=self)
                )
            return
        super().send(bcp_command, kwargs)

    def send_goodbye(self):
        if self._sender is None:
            return
        super().send_goodbye()

    def stop(self):
        if self._sender is None:
            return
        super().stop()
