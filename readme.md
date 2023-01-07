## Major tools used in building this Auction and Bidding system are Python's web framework called Flask which is used for developing REST APIs and PostMan (a platform for building and using APIs).   

<br/>

### All the routes available in these APIs are created with different request methods like `GET`,`POST`,`DELETE`, and `PUT`.   
 
<br/>

## Techstack:
1. Python Web Framework (Flask)
2. VS Code
3. Docker
4. SQLite
5. POSTMAN (API development Aplatform)

<br/>

## Run the Application without DOCKER
1. Download the folder with all the files.
2. Navigate to the folder using CMD.
3. Run cmd `pip install -r requirements.txt` to install all the required python libraries. (Make sure python is also installed in your system)
4. And then run cmd  `python app.py`.
5. Then the API server will be running on the port address shown on the OUTPUT
6. The APIs can be tested only on the API development platforms like POSTMAN.

<br/>

## Run the Application with DOCKER
1. Download the folder with all the files.
2. Navigate to the folder using CMD.
3. Run cmd `docker build --tag <Enter the name of WORKDIR> .` to Build a Docker Image.
4. Run cmd `docker images` to view list of all the docker repositories.
5. Run cmd `docker run -d -p 5000:5000 <Enter the name of WORKDIR>` to run an image as a container.
6. Then the API server will be running on the port address shown on the OUTPUT
7. The APIs can be tested only on the API development platforms like POSTMAN.

<br/>

## Have access to PostMan collection of these APIs with the link below
* https://documenter.getpostman.com/view/21857595/2s8YzUx1mJ

<br/>

## API token login credentials:
- Admin name: Admin
- Admin password: Password

- User name: Jeevan
- User password: Jeevan

<br/>

## Important points to be noted:

* A token will be created while logging in and only when token is attached to request header and  is provided along with username and password then only the login in to API will be successful.

* Access token should be added into every API request.


* Noraml users can only access limited number of routes: Access levels are mentioned to the side of API route as shown in below
`@app.route("/BidCreation", methods=["POST"])  # Only Normal User can access this route`

* These above credentials are hashed in the database`

* All the testing images are uploaded in the Testing Images folder in the current directory.`
