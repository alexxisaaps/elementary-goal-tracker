#!/usr/bin/env python3

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Granite', '7.0')

try:
    from goaltracker import main
    sys.exit(main())
except Exception as e:
    import traceback
    error_msg = traceback.format_exc()
    print(f"Fatal error: {error_msg}", file=sys.stderr)
    sys.exit(1)