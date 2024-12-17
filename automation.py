import subprocess
import sys
import os

def resolve_conflicts():
    try:
        # Check if there are merge conflicts
        status = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if 'both modified:' in status.stdout:
            # If there are conflicts, use ours (--ours) to resolve
            subprocess.run(['git', 'checkout', '--ours', '.'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error resolving conflicts: {str(e)}")
        return False
    return True

def create_new_branch(base_branch, new_branch):
    try:
        # Fetch the latest changes
        subprocess.run(['git', 'fetch'], check=True)
        
        # Save current branch
        current = subprocess.run(['git', 'branch', '--show-current'], 
                               capture_output=True, text=True).stdout.strip()
        
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
            # Save changes
            subprocess.run(['git', 'stash'], check=True)
            
            try:
                # Checkout existing branch
                subprocess.run(['git', 'checkout', new_branch], check=True)
                
                # Try to apply stashed changes
                stash_result = subprocess.run(['git', 'stash', 'pop'], 
                                           capture_output=True, 
                                           text=True, 
                                           check=False)
                
                if stash_result.returncode != 0:
                    # If there were conflicts, resolve them
                    if not resolve_conflicts():
                        print("Failed to resolve conflicts")
                        return False
            except Exception as e:
                print(f"Error during branch operations: {str(e)}")
                # Try to return to original branch
                subprocess.run(['git', 'checkout', current], check=False)
                return False
        else:
            # Save changes
            subprocess.run(['git', 'stash'], check=True)
            
            try:
                # Checkout base branch
                subprocess.run(['git', 'checkout', base_branch], check=True)
                
                # Pull latest changes
                subprocess.run(['git', 'pull', 'origin', base_branch], check=True)
                
                # Create and checkout new branch
                subprocess.run(['git', 'checkout', '-b', new_branch], check=True)
                
                # Apply stashed changes
                subprocess.run(['git', 'stash', 'pop'], check=True)
            except Exception as e:
                print(f"Error during branch operations: {str(e)}")
                # Try to return to original branch
                subprocess.run(['git', 'checkout', current], check=False)
                return False
        
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
