"""Write documentation"""

import json

# Load strings.json
strings = json.load(open("custom_components/teslemetry/strings.json"))
en = json.load(open("custom_components/teslemetry/translations/en.json"))
icons = json.load(open("custom_components/teslemetry/icons.json"))

# Sort keys
open("custom_components/teslemetry/strings.json", "w").write(
    json.dumps(strings, indent=2, sort_keys=True)
)
open("custom_components/teslemetry/translations/en.json", "w").write(
    json.dumps(en, indent=2, sort_keys=True)
)
open("custom_components/teslemetry/icons.json", "w").write(
    json.dumps(icons, indent=2, sort_keys=True)
)
