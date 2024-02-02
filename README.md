# Moodloc

Backend application that tracks persons mood based on their location. The goal of it is to determine where the user is most happy, most sad or content.
Fixed locations should be provided:
- Home
- Work
- Gym

Your cellphone sends an information about the selfie:
- Location (can be any location)
- Person mood (happy, content, sad)

Information is sent as a JSON payload in a form (example):
POST /capture
```
{
	"mood": "happy",
	"location": {
		"north": "44.770174",
		"south": "17.190928"
	 }
}
```

Backend should calculate the nearest place (home, work or gym) and store following information into the database:

- mood
- closeTo (home, work, gym)
- locationNorth
- locationSouth

GET /statistics/mood



### *List of content:*

* **Introduction**
* **Toolkit**
* **Installation guide**
* **API specification**
* **References**

### *Introduction*

* The WebAPI backend application written in Python Flask framework.
* Data storage is SQLite with: 
	* Code First approach;
	* Flask SQLAlchemy ORM;
	* Flask Migrate for database migrations;
	* **Notice!** For real-time use, use MySQL database;
* Image storage:
	* File system;
	* **Notice!** For real-time use, use CDN;
* Authentication and Authorization: 
	* JTW Bearer token issuance based on login credentials.

* Third Party modules: 
	* PyJWT - Handles JWT token jobs, used for Authorization.
	* GPSPhoto - High level library for extracting GPS data from photos
	* Geopy - For retrieving data about GPS coordinates.
	* EmotionRecognition - Used to extract emotions from selfies. More on this [link](https://github.com/atulapra/Emotion-detection).

### *Toolkit*
* VS Code - Code editor.
* Postman - Calling the API.
* DB Browser (SQLite) - Database management program with nice GUI.

### *Installation Guide*

1. Install `python3.7.5` and `pip`.
2. Install `pipenv`
3. Navigate to the root folder of the application and open terminal.
4. Activate environment with `pipenv shell`
5. Install dependencies from `pipfile` with `pipenv install`. This can take some time.
6. Download models from [this](https://drive.google.com/file/d/1rdgSdMcXIvfoPmf702UCtH6RNcvkKFu7/view) link and put them into `emotion_util` folder.
7. Run the app with `flask run`

### *API Specification*

#### Key data structures: 
	- Users
	- Places
	- Captures

* Users can register, login and retrieve their information.
* Places are a set of locations that the user flagged as home, work or something else.
* Captures are mood and location records based on user selfies. 

#### Validation

* Validation is implemented by usage of decorators, input restrictions and handling Exceptions.

#### Endpoints:
* POST /authorize - Provides JWT token on successful login. Token lasts for 30 minutes.
* POST /user - Creates a new user.
* GET /user - Get user metadata.
* POST /place - Add new user place.
* GET /place - Get a list of user places.
* POST /capture - Upload user selfie and saves mood and location information based on it.
* GET /statistics/mood - Get percentage of each emotion for specific user based on captures.
* GET /statistics/state-of-mind - Get overtime emotional progress for user based on captures.
* GET /statistics/happiness - Get proximity to user places based on captures where the user was happy.

#### *References*

- [https://docs.python.org/3/](https://docs.python.org/3/)
- [http://flask.palletsprojects.com/en/1.1.x/](http://flask.palletsprojects.com/en/1.1.x/)
- [https://github.com/atulapra/Emotion-detection](https://github.com/atulapra/Emotion-detection)
- [https://www.sylvaindurand.org/gps-data-from-photos-with-python/](https://www.sylvaindurand.org/gps-data-from-photos-with-python/)

#### *Trivia*
* Name Moodloc references World of Warcraft creature called Murloc.
* Special thanks to the `dir()` command.