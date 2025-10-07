#!/bin/bash
# YSA Signal Release Script
# Automates version bumping, building, and uploading to PyPI
# Email jacobbcahoon@gmail.com if you ever need to upload a new version

set -e # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
  echo -e "\n${BLUE}==>${NC} ${GREEN}$1${NC}"
}

print_error() {
  echo -e "${RED}Error: $1${NC}"
}

print_warning() {
  echo -e "${YELLOW}Warning: $1${NC}"
}

# Check if we're in a git repository
if [ ! -d .git ]; then
  print_error "Not in a git repository!"
  exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  print_warning "You have uncommitted changes."
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

# Get current version from setup.py
CURRENT_VERSION=$(grep "version=" setup.py | head -1 | sed "s/.*version='\([^']*\)'.*/\1/")
print_step "Current version: $CURRENT_VERSION"

# Ask for version bump type
echo ""
echo "Select version bump type:"
echo "  1) Patch (${CURRENT_VERSION} -> ${CURRENT_VERSION%.*}.$((${CURRENT_VERSION##*.} + 1)))"
echo "  2) Minor (${CURRENT_VERSION} -> ${CURRENT_VERSION%.*.*}.$((${CURRENT_VERSION##*.*.} + 1)).0)"
echo "  3) Major (${CURRENT_VERSION} -> $((${CURRENT_VERSION%%.*.*} + 1)).0.0)"
echo "  4) Custom"
echo "  5) Skip version bump"
read -p "Choice (1-5): " VERSION_CHOICE

case $VERSION_CHOICE in
1)
  # Patch bump
  NEW_VERSION="${CURRENT_VERSION%.*}.$((${CURRENT_VERSION##*.} + 1))"
  ;;
2)
  # Minor bump
  MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
  MINOR=$(echo $CURRENT_VERSION | cut -d. -f2)
  NEW_VERSION="${MAJOR}.$((MINOR + 1)).0"
  ;;
3)
  # Major bump
  MAJOR=$(echo $CURRENT_VERSION | cut -d. -f1)
  NEW_VERSION="$((MAJOR + 1)).0.0"
  ;;
4)
  # Custom version
  read -p "Enter new version: " NEW_VERSION
  ;;
5)
  # Skip version bump
  NEW_VERSION=$CURRENT_VERSION
  print_warning "Skipping version bump"
  ;;
*)
  print_error "Invalid choice"
  exit 1
  ;;
esac

if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
  print_step "Bumping version from $CURRENT_VERSION to $NEW_VERSION"

  # Update version in all files
  sed -i '' "s/version.*=.*\"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
  sed -i '' "s/version='$CURRENT_VERSION'/version='$NEW_VERSION'/" setup.py
  sed -i '' "s/__version__ = '$CURRENT_VERSION'/__version__ = '$NEW_VERSION'/" __init__.py

  print_step "Updated version in pyproject.toml, setup.py, and __init__.py"
fi

# Run tests
print_step "Running tests..."
if command -v pytest &>/dev/null; then
  pytest tests/ -v
  if [ $? -ne 0 ]; then
    print_error "Tests failed! Aborting release."
    exit 1
  fi
else
  print_warning "pytest not found, skipping tests"
fi

# Clean old builds
print_step "Cleaning old build artifacts..."
rm -rf dist/ build/ *.egg-info

# Build the package
print_step "Building package..."
if [ -d venv ]; then
  source venv/bin/activate
fi

python -m build

if [ $? -ne 0 ]; then
  print_error "Build failed!"
  exit 1
fi

# Check the distribution
print_step "Checking distribution..."
twine check dist/*

if [ $? -ne 0 ]; then
  print_error "Distribution check failed!"
  exit 1
fi

# Show what will be uploaded
print_step "Files to upload:"
ls -lh dist/

# Ask for confirmation
echo ""
read -p "Upload to PyPI? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted. Files are ready in dist/ if you want to upload manually."
  exit 0
fi

# Upload to PyPI
print_step "Uploading to PyPI..."
twine upload dist/*

if [ $? -ne 0 ]; then
  print_error "Upload failed!"
  exit 1
fi

print_step "✓ Successfully released version $NEW_VERSION to PyPI!"

# Ask to commit and tag
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
  echo ""
  read -p "Create git commit and tag for v$NEW_VERSION? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add setup.py pyproject.toml __init__.py
    git commit -m "Release v$NEW_VERSION"
    git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
    print_step "✓ Created commit and tag v$NEW_VERSION"

    read -p "Push to remote? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      git push && git push --tags
      print_step "✓ Pushed to remote"
    fi
  fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║      Release Complete! 🎉              ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Package: ysa-signal"
echo "Version: $NEW_VERSION"
echo "PyPI: https://pypi.org/project/ysa-signal/$NEW_VERSION/"
echo ""
echo "Users can now install with:"
echo "  pip install ysa-signal==$NEW_VERSION"
echo ""
