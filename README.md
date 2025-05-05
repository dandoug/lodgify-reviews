# Lodgify Reviews

- [Lodgify Reviews](#lodgify-reviews)
  - [Background](#background)
    - [Disclaimer](#disclaimer)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Python environment](#python-environment)
    - [Authorization](#authorization)
  - [Scripts](#scripts)
    - [download_reviews.py](#download_reviewspy)
      - [Usage](#usage)
      - [Options](#options)
      - [Examples](#examples)
    - [import_reviews.py](#import_reviewspy)
      - [Input file formats](#input-file-formats)
        - [.csv files](#csv-files)
        - [.json files](#json-files)
      - [Usage](#usage-1)
      - [Options](#options-1)
      - [Examples](#examples-1)
    - [delete_reviews.py](#delete_reviewspy)
      - [Usage](#usage-2)
      - [Options](#options-2)
      - [Examples](#examples-2)
  - [Data](#data)



## Background
My need for the code here came from the fact that I was migrating my short-term rental website from a WordPress site using the [Motopress HotelBooking plugin](https://motopress.com/products/hotel-booking) to [Lodgify](https://www.lodgify.com/).  On that site, I'd gathered my property's reviews from [VRBO](https://vrbo.com/) previously using [WP Review Slider](https://wpreviewslider.com/). So, I had all the review data in my database.  That review plugin has an option to export it all as a .csv file and that's where [reviewdata.csv](data/reviewdata.csv) came from.

I also discovered that the current Lodgify implementation shows reviews in a default order of "most recently created" first.  That makes sense for reviews organically created by guests, but when the reviews are created by importing from another platform, sorting in reverse order by `stayDate` makes more sense.  Sadly, at least as I write this, that option was not availabe.  I discovered that after importing about half of my reviews. 

What I needed to do is delete them all the reviews I had already in Lodgify and recreate them from my data in the right order so that sorting by "creation" date (i.e. when I created them in Lodgify) results in the same ordering as sorting by `stayDate` (i.e. when that guest stayed at the property).  That will make the places where Lodgify display "recent" reviews actually show reviews from guests that stayed recently.

### Disclaimer
I created this project to manage and manipulate my set of Lodgify reviews using the non-public (at the time of this writing) v3 and v4 APIs from Lodgify.  They are not officially supported and I had to reverse engineer them from observing what the website uses.  The notes here are really for "future me".  This isn't a project I'm looking to maintain or support.  I'm not looking for collaborators or feature requests.  If it helps you, great. 

## Setup

### Prerequisites
I developed this project on a laptop running macOS Sequoia 15.4.1 (ARM) using python 3.11.11 installed via [pyenv](https://github.com/pyenv/pyenv) which itself was intalled using [homebrew](https://brew.sh/).  That's my starting point.  You might need to adjust for your environment.

### Python environment
As a one-time setup, after cloning this repo and switching to the root directory, create the virtual environment and activate it
```bash
python -m venv .venv
source .venv/bin/activate
```
Now add the necessary dependencies
```bash
pip install -r requirements.txt
```

When you no longer need the environment active, you can exit it with
```bash
deactivate
```

After setting it up, you only need to 
```bash
source .venv/bin/activate
```
to activate the environment and use from the command line.

### Authorization

The APIs used by this project require a [bearer authorization token](https://swagger.io/docs/specification/v3_0/authentication/bearer-authentication/).  A valid value of for such a token is never going to be checked into source control for this project, so don't even bother looking for it.  If you're using this code, you can obtain a value for this token by inspecting the browser request (using Developer Tools) when interacting with https://app.lodgify.com/reviews/website.

Once you have a token value, copy the file [.env.sample](.env.sample) to a new file named `.env` and edit the file to save your token on the line that begins with `AUTH_TOKEN=`.  Store your value on the same line, don't introduce any whitespace.

During execution, this value will be loaded by the code using `load_dotenv` from the [dotenv module](https://pypi.org/project/python-dotenv/) and be available as a environment variable named `AUTH_TOKEN`.

## Scripts

The functions performed here are divided into standalone scripts that can be executed from the command line after creating and activating the python environment as described [above](#python-environment).

Run a script from the top level directory of this project using a command like
```bash
python scripts/delete_reviews.py --review 394007 --prop 669875
```

<p><br/></p>

### List of scripts
* [download_reviews.py](#download_reviewspy)
* [delete_reviews.py](#delete_reviewspy)
* [import_reviews.py](#import_reviewspy)



### download_reviews.py
This script will download a single review or all the reviews for an account.  

#### Usage
```bash
download_reviews.py [-h] [--review REVIEW] [--prop PROP] [--output OUTPUT]
```
#### Options
<dl>
  <dt>-h, --help</dt>     
  <dd>show this help message and exit</dd>

  <dt>--review <code>REVIEW</code></dt>  
  <dd>int32 id of review to download, optional if getting all</dd>

  <dt>--prop <code>PROP</code></dt>      
  <dd>int32 id of property, ignored if <code>--review</code> is not specified, defaults to <code>PROP_ID</code> environment var</dd>

  <dt>--output <code>OUTPUT</code></dt>      
  <dd>file to write downloaded reviews to, defaults to <code>stdout</code></dd>
</dl>

#### Examples

Download review id `1234` from property id `4567` and write output to console
```bash
python scripts/download_reviews.py --review 1234 --prop 4567
```

Download review id `1234` from the default property id and output to console
```bash
python scripts/downlaod_reviews.py --review 1234
```

Download all reviews for account and write to file `reviews.json`
```bash
python scripts/download_reviews.py --output reviews.json
```

### import_reviews.py
This script will import reviews from a file.  The file is in one of two formats and the choice is indicated by the extension of the input filename.  In either case, the process will create one review at a time and messages about the reesults and errors will be sent to the console.

#### Input file formats

##### .csv files

These files are .csv files as downloaded from the  [WP Review Slider](https://wpreviewslider.com/) WordPress plugin.  The use case here is migrating reviews from another site into Lodgify.  The file will have a header row.  Each row represents a review to create and the following columns will be used

* **created_time** - this is the date when the original review was created.  The import process will strip just the year and month from this and use that as the `stayDate` input.  For example, if the .csv file contains `2024-02-20 00:00:00`, we'll use `2024-02` as the `stayDate`.
* **reviewer_name** - this will be mapped to `guestName` in the Lodgify review
* **rating** - this int is the `rating` for Lodgify as well
* **review_text** - this is the `text` field of the Lodgify review
* **type** - this is the `source` field in the Lodgify reivew
* **review_title** - this is the `title` field in the Lodgify review

For the purpose of this import, some of the other fields required for Lodgify are not present in the .csv file, so these defaults will be supplied

* `guestType` - `Group`
* `guestCountry` - `US`
* `guestEmail` - empty string
* `roomName` - empty string, the property I'm working on doesn't have rooms, whole house rental

The `propertyId` used for the review will come from the command-line argument or the environment.

##### .json files

These files will contain a list objects that were saved from Lodgify and each one will have all the required fields specified so no mapping is required.  The `propertyId` is available in the file as part of each review.  The review id's in the file are ignored and the data is used to create new reviews, one at a time.

#### Usage
```bash
import_reviews.py [-h] [--prop PROP] [--reviews REVIEWS]
```
#### Options
<dl>
  <dt>-h, --help</dt>     
  <dd>show this help message and exit</dd>

  <dt>--prop <code>PROP</code></dt>      
  <dd>int32 id of property, ignored for .json files, defaults to <code>PROP_ID</code> environment var</dd>

  <dt>--reviews <code>REVIEWS</code></dt>  
  <dd>file containing reviews to import, either .csv or .json</dd>
</dl>

#### Examples

Import a set of reviews from file `backup.csv` for property id `4567`
```bash
python scripts/import_reviews.py --reviews backup.csv --prop 4567
```

Import the reviews from `reviews.json`
```bash
python scripts/downlaod_reviews.py --reviews reviews.json
```

### delete_reviews.py
This script will delete a single review or all the reviews for an account.  Use with care this is pretty destructive.  It might be a good practice [backup the reviews first](#download_reviewspy).


#### Usage
```bash
delete_reviews.py [-h] [--review REVIEW] [--prop PROP]
```
#### Options
<dl>
  <dt>-h, --help</dt>     
  <dd>show this help message and exit</dd>

  <dt>--review <code>REVIEW</code></dt>  
  <dd>int32 id of review to delete, optional if deleting all</dd>

  <dt>--prop <code>PROP</code></dt>      
  <dd>int32 id of property, ignored if <code>--review</code> is not specified, defaults to <code>PROP_ID</code> environment var</dd>
</dl>

#### Examples

Delete review id `1234` from property id `4567`
```bash
python scripts/delete_reviews.py --review 1234 --prop 4567
```

Delete review id `1234` from the default property id from `PROP_ID` environment variable or `.env` file.
```bash
python scripts/delete_reviews.py --review 1234
```

Delete all reviews for account.
```bash
python scripts/delete_reviews.py
```




## Data

There's a [reviewdata.csv](data/reviewdata.csv) file with raw review data that will be used in the code in this project.

There's also a [collection export file](data/Lodgify%20V3-V4%20Reviews%20API.postman_collection.json) file that can be imported into [Postman](https://www.postman.com/) for interactive work with the APIs.