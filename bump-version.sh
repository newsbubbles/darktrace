#!/bin/bash

# bump-version.sh - Automated version bumping and release script for tracelight
# Usage: 
#   ./bump-version.sh                    # Auto-bump patch version (e.g., 0.1.1 -> 0.1.2)
#   ./bump-version.sh 0.2.0              # Set specific version
#   ./bump-version.sh minor              # Bump minor version (e.g., 0.1.1 -> 0.2.0)
#   ./bump-version.sh major              # Bump major version (e.g., 0.1.1 -> 1.0.0)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
fi

# Check if working directory is clean
if ! git diff-index --quiet HEAD --; then
    print_error "Working directory is not clean. Please commit or stash changes first."
fi

# Get current version from pyproject.toml
get_current_version() {
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found!"
    fi
    
    current_version=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
    if [ -z "$current_version" ]; then
        print_error "Could not find version in pyproject.toml"
    fi
    echo "$current_version"
}

# Parse version into components
parse_version() {
    local version=$1
    if [[ ! $version =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
        print_error "Invalid version format: $version (expected: X.Y.Z)"
    fi
    
    major=${BASH_REMATCH[1]}
    minor=${BASH_REMATCH[2]}
    patch=${BASH_REMATCH[3]}
}

# Calculate new version based on bump type
calculate_new_version() {
    local current_version=$1
    local bump_type=$2
    
    parse_version "$current_version"
    
    case $bump_type in
        "patch"|"")
            new_patch=$((patch + 1))
            echo "${major}.${minor}.${new_patch}"
            ;;
        "minor")
            new_minor=$((minor + 1))
            echo "${major}.${new_minor}.0"
            ;;
        "major")
            new_major=$((major + 1))
            echo "${new_major}.0.0"
            ;;
        *)
            # Assume it's a specific version
            if [[ $bump_type =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                echo "$bump_type"
            else
                print_error "Invalid bump type or version: $bump_type"
            fi
            ;;
    esac
}

# Update version in files
update_version_in_files() {
    local new_version=$1
    
    print_status "Updating version to $new_version in pyproject.toml..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed
        sed -i '' "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
    else
        # Linux sed
        sed -i "s/^version = \".*\"/version = \"$new_version\"/" pyproject.toml
    fi
    
    print_status "Updating version to $new_version in src/tracelight/__init__.py..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS sed
        sed -i '' "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" src/tracelight/__init__.py
    else
        # Linux sed
        sed -i "s/^__version__ = \".*\"/__version__ = \"$new_version\"/" src/tracelight/__init__.py
    fi
}

# Main script logic
main() {
    local bump_arg="${1:-patch}"
    
    print_status "Starting version bump process..."
    
    # Get current version
    current_version=$(get_current_version)
    print_status "Current version: $current_version"
    
    # Calculate new version
    new_version=$(calculate_new_version "$current_version" "$bump_arg")
    print_status "New version: $new_version"
    
    # Confirm with user
    echo
    print_warning "About to bump version from $current_version to $new_version"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Version bump cancelled."
        exit 0
    fi
    
    # Update version in files
    update_version_in_files "$new_version"
    
    # Commit changes
    print_status "Committing version bump..."
    git add pyproject.toml src/tracelight/__init__.py
    git commit -m "Bump version to $new_version"
    
    # Create and push tag
    print_status "Creating git tag v$new_version..."
    git tag -a "v$new_version" -m "Release version $new_version"
    
    print_status "Pushing changes and tag to origin..."
    git push origin main
    git push origin "v$new_version"
    
    print_success "Version bump complete!"
    print_success "Version: $current_version → $new_version"
    print_success "Tag: v$new_version created and pushed"
    print_success "GitHub Actions should now build and publish to PyPI"
    
    echo
    print_status "You can monitor the release at:"
    echo "  GitHub Actions: https://github.com/$(git remote get-url origin | sed 's/.*github[^:]*:\([^.]*\).*/\1/')/actions"
    echo "  PyPI: https://pypi.org/project/tracelight/"
}

# Show usage if --help is passed
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [VERSION|BUMP_TYPE]"
    echo
    echo "BUMP_TYPE options:"
    echo "  patch (default) - Increment patch version (0.1.1 → 0.1.2)"
    echo "  minor          - Increment minor version (0.1.1 → 0.2.0)"
    echo "  major          - Increment major version (0.1.1 → 1.0.0)"
    echo
    echo "VERSION format:"
    echo "  X.Y.Z          - Set specific version (e.g., 1.2.3)"
    echo
    echo "Examples:"
    echo "  $0              # Auto-bump patch version"
    echo "  $0 patch        # Explicit patch bump"
    echo "  $0 minor        # Bump minor version"
    echo "  $0 major        # Bump major version"
    echo "  $0 2.0.0        # Set to specific version"
    exit 0
fi

# Run main function
main "$@"