#!/usr/bin/env python3

import logging
import re
import sys
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

CURRENT_YEAR = datetime.today().year

LICENSE_BLOB = """Copyright (c) %d The Jaeger Authors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.""" % CURRENT_YEAR

LICENSE_BLOB_LINES_GO = [
    ('// ' + l).strip() + '\n' for l in LICENSE_BLOB.split('\n')
]

COPYRIGHT_RE = re.compile(r'Copyright \(c\) (\d+)', re.I)


def update_go_license(name, force=False):
    with open(name) as f:
        orig_lines = list(f)
    lines = list(orig_lines)

    found = False
    changed = False
    jaeger = False
    for i, line in enumerate(lines[:5]):
        m = COPYRIGHT_RE.search(line)
        if not m:
            continue

        found = True
        jaeger = 'Jaeger' in line

        year = int(m.group(1))
        if year == CURRENT_YEAR:
            break

        # Avoid updating the copyright year.
        #
        # new_line = COPYRIGHT_RE.sub('Copyright (c) %d' % CURRENT_YEAR, line)
        # assert line != new_line, ('Could not change year in: %s' % line)
        # lines[i] = new_line
        # changed = True
        break

    # print('found=%s, changed=%s, jaeger=%s' % (found, changed, jaeger))

    def replace(header_lines):
        if 'Code generated by' in lines[0]:
            lines[1:1] = ['\n'] + header_lines
        else:
            lines[0:0] = header_lines

    if not found:
        replace(LICENSE_BLOB_LINES_GO + ['\n'])
        changed = True
    else:
        if not jaeger:
            replace(LICENSE_BLOB_LINES_GO[0])
            changed = True

    if changed:
        with open(name, 'w') as f:
            for line in lines:
                f.write(line)
        print(name)


def main():
    if len(sys.argv) == 1:
        print('USAGE: %s FILE ...' % sys.argv[0])
        sys.exit(1)

    for name in sys.argv[1:]:
        if name.endswith('.go'):
            try:
                update_go_license(name)
            except Exception as error:
                logger.error('Failed to process file %s', name)
                logger.exception(error)
                raise error
        else:
            raise NotImplementedError('Unsupported file type: %s' % name)


if __name__ == "__main__":
    main()
