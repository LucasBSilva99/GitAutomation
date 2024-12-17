import subprocess
import sys
import os

def create_new_branch(base_branch, new_branch):
    try:
        # Fetch the latest changes
        subprocess.run(['git', 'fetch'], check=True)
        
        # Check if base branch exists
        result = subprocess.run(['git', 'branch', '--list', base_branch], 
                              capture_output=True, 
                              text=True)
        if not result.stdout.strip():
            print(f"Error: Base branch '{base_branch}' does not exist.")
            return False
        
        # Check if new branch already exists
        result = subprocess.run(['git', 'branch', '--list', new_branch], 
                              capture_output=True, 
                              text=True)
        
        if result.stdout.strip():
            print(f"Branch '{new_branch}' already exists. Checking out and pushing changes...")
            # Checkout existing branch
            subprocess.run(['git', 'checkout', new_branch], check=True)
        else:
            # Checkout base branch
            subprocess.run(['git', 'checkout', base_branch], check=True)
            
            # Pull latest changes
            subprocess.run(['git', 'pull', 'origin', base_branch], check=True)
            
            # Create and checkout new branch
            subprocess.run(['git', 'checkout', '-b', new_branch], check=True)
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are changes to commit
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if status.stdout.strip():
            # Commit changes
            subprocess.run(['git', 'commit', '-m', f'Update for branch {new_branch}'], check=True)
            
            # Push the changes
            subprocess.run(['git', 'push', 'origin', new_branch], check=True)
            print(f"Successfully committed and pushed changes to branch '{new_branch}'")
        else:
            print("No changes to commit")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {str(e)}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python automation.py <base_branch> <new_branch>")
        sys.exit(1)
    
    base_branch = sys.argv[1]
    new_branch = sys.argv[2]
    
    if not os.path.exists('.git'):
        print("Error: Not a git repository")
        sys.exit(1)
    
    success = create_new_branch(base_branch, new_branch)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
