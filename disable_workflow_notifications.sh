#!/bin/bash

# List of your 9 TEP repositories
REPOS=(
  "matthewsmawfield/TEP-Theory"
  "matthewsmawfield/TEP-GNSS-Multi"
  "matthewsmawfield/TEP-GNSS-Long"
  "matthewsmawfield/TEP-GNSS-RINEX"
  "matthewsmawfield/TEP-GL"
  "matthewsmawfield/TEP-GTE"
  "matthewsmawfield/TEP-UCD"
  "matthewsmawfield/TEP-RBH"
  "matthewsmawfield/TEP-SLR"
)

echo "Disabling workflow notifications for all TEP repositories..."

for repo in "${REPOS[@]}"; do
  echo "Processing $repo..."
  # Set repository to ignored (stops all notifications)
  gh api -X PUT "/repos/$repo/subscription" -f ignored=true 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "✓ $repo notifications disabled"
  else
    echo "✗ Failed to update $repo (may need to check manually)"
  fi
done

echo ""
echo "Done! You can verify at: https://github.com/watching"
