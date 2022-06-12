# Red-Yoinker
If you are not a programmer, you may want to use [this tool](https://redditdownloader.github.io/) instead (NOTE: that website is not made by me). It has a GUI meaning that it is a normal application like a Music Player or Microsoft Words with visuals instead of a command line application where you need to type your commands. It also does similar things as this app, so you are not missing on anything.

Red-Yoinker is a CLI app to download images and videos from reddit.com. This app has 2 different subcommands: **scrap** and **history**. The scrap subcommand will allow you to analyze or download content from your favorite subreddits while the history subcommand will allow you to keep track of downloaded content and any media which could not be downloaded. It will also allow you to retry downloading them. The **usage** section will go in depth on what each subcommand and option does.

### Dependencies
If you want to use the source code, you will have to use [ratelimit](https://pypi.org/project/ratelimit/) or remove it's uses from [mediadownloader.py](https://github.com/maxensdestine/Red-Yoinker/blob/main/mediadownloader.py) and [pushshiftscrapper.py](https://github.com/maxensdestine/Red-Yoinker/blob/main/pushshiftscrapper.py) (the @limit annotations). Please know that not using rate limits may cause the program to be unable to download many images and videos.

### Limits of This App
This app cannot download media from every submission. The supported format are currently: content hosted on reddit (images, videos) including galleries, imgur links to single images, imgur link to galleries (sometimes fails). Also, the min score and max score use the values from pushshift which are often different than the real ones. This is because pushshift does not update these numbers after storing a submission on their servers. You can still use those options, but keep in mind that they are mostly incorrect, especially for large numbers.

## Usage
### Calling Examples
You must use scrap or history, but not both at the same time. The general options must come before the any of the subcommands and their options.
Here is an example which displays the name of the first 50 submissions with at least 10 upvotes, posted between 2018 August 30 and 2020 September 24, from the subreddits movie and nba and also store them in the history: `python3 redyoinker.py -subs "movie nba" scrap -t 1 -r 4 -sm 10 -s 50 -b 2020-09-24 -a "2018-08-30 -h -ti" `
Here is another example which displays the full link and downloads media (images or videos) of the first 8 submissions with at least 3 upvotes, posted between 2018 August 30 and 2020 September 24 from the subreddits movie and nba and also store them in the history: `python3 redyoinker.py -subs "movie nba" scrap -t 1 -r 4 -sm 3 -s 8 -b 2020-09-24 -a "2018-08-30 -h -fl -d "/home/mydirectory/" `
### General Options
| calling syntax (--..) | short syntax (-..) | description                                                                                                                                                                                   | default value                                          | example of valid input  | example of invalid input |
|-----------------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|-------------------------|--------------------------|
| subreddits            | subs               | The name of all subreddits to include in the command, seperated by spaces (e.g. "askreddit pcgamers linux"). Must match exactly the name as it is on reddit for the history to work properly. | N/A (it will consider submissions from all subreddits) | -subs "movie sport nba" | "movie,sport,nba"        |
| verbose               | v                  | Use this flag to display execution logs. Does not give a value to this option, just use it.                                                                                                   | False (Logs are not displayed)                         | -v                      | -v true                  |
### Subcommand Scrap
| calling syntax (--..) | short syntax (-..) | description                                                                                                                                                                                                                                                                                                                                                                              | default value                            | example of valid input   | example of invalid input                                                                                   |
|-----------------------|--------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|--------------------------|------------------------------------------------------------------------------------------------------------|
| timeout               | t                  | How long to wait, in seconds, after a request fails                                                                                                                                                                                                                                                                                                                                      | 2                                        | -t 6                     | -t 1s                                                                                                      |
| maxrepeat             | r                  | The maximum number of times to retry a request before giving up                                                                                                                                                                                                                                                                                                                          | 3                                        | -r 2                     | -r "5 times"                                                                                               |
| minscore              | sm                 | The minimum amount of point that a post needs to be included                                                                                                                                                                                                                                                                                                                             | 1                                        | -sm 4                    | -sm "6 upvotes"                                                                                            |
| maxscore              | sx                 | The maximum amount of point that a post can have to be included                                                                                                                                                                                                                                                                                                                          | ∞ (infinity)                             | -sx 100                  | -sx "-100"                                                                                                 |
| size                  | s                  | The number of results wanted. Use 0/inf/infinity to get as many as are returned                                                                                                                                                                                                                                                                                                          | 25                                       | -s 100                   | -s -1                                                                                                      |
| after                | a                  | The maximum (inclusive) creation date a post can have to be included in ISO 8601 format, i.e. yyyy-mm-dd [hh:mm:ss.mmm]. Hours, minutes and seconds are optional. Milliseconds will be ignored though they can be included.                                                                                                                                                              | 2015-05-31 (reddit's creation date)      | -a 2020-09-20            | -a 2020 (invalid because there should be at least a year, month and date)                                  |
| before                 | b                  | The minimum (inclusive) creation date a post can have to be included in ISO 8601 format, i.e. yyyy-mm-dd [hh:mm:ss.mmm]. Hours, minutes and seconds are optional. Milliseconds can be included but they will be ignored.                                                                                                                                                                 | Time at the moment the program is called | -b "2020-08-31 15:17:32" | -b 2020-04-12 14:54:12 (invalid because when there is a space the value must be surrounded by parenthesis) |
| title                 | ti                 | Use this flag to display the posts titles                                                                                                                                                                                                                                                                                                                                                | False (titles not displayed)             | -ti                      | --title 2 (invalid because this flag needs no value)                                                       |
| murl                  | u                  | Use this flag to display the posts' media urls (urls to directly access the images/videos in the post)                                                                                                                                                                                                                                                                                   | False (media urls not displayed)         | --murl                   | --murl "32" (invalid because this flag needs no value)                                                     |
| flink                 | fl                 | Use this flag to display the posts full links                                                                                                                                                                                                                                                                                                                                            | False (full links not displayed)         | --flink                  | --flink 46 (invalid because this flag needs no value)                                                      |
| json                  | js                 | Use this flag to display the json of submission                                                                                                                                                                                                                                                                                                                                          | False (json not displayed)               | -js                      | --json "pepe" (invalid because this flag needs no value)                                                   |
| history               | ht                 | Use this flag to save the results in history and exclude those who are already in history                                                                                                                                                                                                                                                                                                | False (results not stored in history)    | -ht                      | --history 2 (invalid because this flag needs no value)                                                     |
| retryfails            | rfail              | Use this flag to try to download again using the failed download history. No other action will be taken. Use the other flags as usual for download directory, timeout, etc. If no download directory is given, the directory of this script will be used. Use the empty string with the subreddit flag to retry for all eligible subreddits (subreddits shown with the --showfail flag). | False (does not retry)                   | --retryfails             | -rfails /home/dir/ (invalid because this flag needs no value)                                              |
| download              | d                  | The folder where to download files. If not used (or empty string), media will not be downloaded.                                                                                                                                                                                                                                                                                         | False (media not downloaded)             | --download /home/dir/    | --download                                                                                                 |

### Subcommand History
| calling syntax (--..) | short syntax (-..) | description                                                                                                                                                                                                                                         | default value                         | example of valid input | example of invalid input |
|-----------------------|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|------------------------|--------------------------|
| clearhist             | cht                | Use this flag to clear the history. No other action will be taken. Only the subreddits flag will be considered with this flag. Use the empty string with the subreddit flag to delete the entire history                                            | False (history is not cleared)        | -cht                   | -cht 12                  |
| showhist              | sht                | Use this flag to show the history and its save location on your machine. No other action will be taken regardless of the other flags used                                                                                                           | False (history is not displayed)      | -sht                   | --sht                    |
| clearfails            | cfail              | Use this flag to clear the failed download history. No other action will be taken. Only the subreddits flag will be considered with this flag. Use the empty string with the subreddit flag to delete the failed download history of all subreddits | False (fail history is not cleared)   | --clearfails           | -clearfail               |
| sfail                 | showfails          | Use this flag to show the number of failed downloads for each subreddit and their save location on your machine. If a subreddit does not appear, it means there are no failures associated with it                                                  | False (fail history is not displayed) | -sfail                 | --sfail                  |
