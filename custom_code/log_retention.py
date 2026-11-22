"""Keep MPF's logs folder small.

Development keeps today's sessions, and always at least the last two. Production (``mpf -P``) keeps only this session's
log, since MPF itself can't be told not to write one.
"""

import datetime
import os
import re

from mpf.core.custom_code import CustomCode

LOG_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-\d{2}-\d{2}-\d{2}-mpf-.*\.log$")
KEEP_SESSIONS = 2


def stale_logs(names, current, production, today):
    """The MPF log names to delete; names start with their timestamp, so they sort by age."""
    logs = sorted((name for name in names if LOG_NAME.match(name)), reverse=True)
    keep = {current}
    if not production:
        keep.update(logs[:KEEP_SESSIONS])
        keep.update(name for name in logs if LOG_NAME.match(name).group(1) == today)
    return [name for name in logs if name not in keep]


def prune(directory, current, production, today):
    removed = 0
    for name in stale_logs(os.listdir(directory), current, production, today):
        try:
            os.remove(os.path.join(directory, name))
            removed += 1
        except OSError:
            pass
    return removed


class LogRetention(CustomCode):
    def on_load(self):
        path = self.machine.options.get("full_logfile_path")
        if not path or not os.path.isdir(os.path.dirname(path)):
            return
        removed = prune(os.path.dirname(path), os.path.basename(path), bool(self.machine.options.get("production")),
                        datetime.date.today().isoformat())
        self.info_log("Removed %s old MPF log(s).", removed)
