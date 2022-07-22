# vimeo-index
Vimeo like other social video platforms, has nice search functionalities. One can search for a video by video name, description or tags. As you can see, these search options are limited. What if we wish to search for a video in which a particular word or phase is uttered inside the video itself? There is no easy way of doing that. That's when this vimeo indexing tool comes along.

This tool, indexes all vimeo videos of an organisation. The goal is to be able to search vimeo videos not only by the apparent text content (i.e. video title, tags and description), but also from the spoken words in the video. 

The web application is created by using Flask. The index is implemented using the whoosh package and speech to text conversion is by the help of Mozila deepspeech.

After cloning the repository, take the following steps to run the project.
1) Make sure python is installed in your systems

2) Change direction into the cloned folder 

3) Create file, name it .env and add the following line into it.
   VIMEO_ACCESS_TOKEN=your organization's vimeo account access token
   VIMEO_CLIENT_ID=your organization's vimeo account client id
   VIMEO_CLIENT_SECRET of your organization's vimeo account client secret.
   
4) Clone the Autosub repository from here https://github.com/abhirooptalasila/AutoSub and extract it inside the vimeo-index folder.The folders structure should look like below.

       -vimeo-indexer
            - AutoSub
                - autosub
                - scripts
                - etc i.e. other files as they appear in the cloned AutoSub
            - templates
            - whoosh_index
            - requirements.txt
            - etc i.e. other files as they appear in the viz-engine folder i have attached in the email.

5) Install all dependecie by running pip3 install -r requirements.txt

6) Run the application as python3 application.py A nice web interface to interact with the indexer will be loaded in your browser. 
