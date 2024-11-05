from flask import Flask, render_template, request
import requests
app = Flask(__name__)


# HOME ROUTE - RENDERS AN HTML TEMPLATE WHERE
# USERS CAN INPUT THEIR GITHUB USERNAME
@app.route("/")
def username():
    return render_template("username.html")


# SUBMIT FUNCTION - PROCESSES A FORM SUBMISSION WITH
# USER DETAILS RENDERING ANOTHER TEMPLATE TO DISPLAY THEM
@app.route("/submit", methods=["POST"])
def submit():
    input_name = request.form.get("name")
    input_age = request.form.get("age")
    return render_template("hello.html", name=input_name, age=input_age)


# RETRIEVES THE GITHUB USERNAME FROM THE SUBMITTED FORM AND CALLS THE
# GET_REPOSITORIES FUNCTION TO FETCH THE USER'S REPOSITORIES
@app.route("/query", methods=["POST"])
def query():
    github_username = request.form.get("github_username")
    response = get_repositories(github_username)
    return render_template("repositories.html", repos=response)


# CONSTRUCTS THE API URL USING THE PROVIDED USERNAME
# MAKES A GET REQUEST TO THE GITHUB API ENDPOINT TO RETRIEVE THE REPOSITORIES
def get_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)

    if response.status_code == 200:
        repos = response.json()
        repo_data = []

        for repo in repos:
            # Get the commits URL
            commits_url = repo["commits_url"].split("{")[0]  # Clean the URL
            commits_response = requests.get(commits_url)

            if commits_response.status_code == 200:
                commits = commits_response.json()
                if commits:  # Check if there are any commits
                    last_commit = commits[0]  # Get the latest commit
                    author = last_commit["commit"]["author"]["name"]
                    message = last_commit["commit"]["message"]
                else:
                    author = "No commits"
                    message = "No commits"
            else:
                author = "Error fetching commits"
                message = "Error fetching commits"

            repo_data.append({
                "name": repo["full_name"],
                "updated_at": repo["updated_at"],
                "author": author,
                "message": message,
                "language": repo.get("language", "N/A")
            })
        return repo_data
    else:
        return [{"name": f"Failed to retrieve repositories: {response.status_code}",
                 "updated_at": "",
                 "author": "",
                 "message": "",
                 "language": ""}]


if __name__ == "__main__":
    app.run(debug=True)
