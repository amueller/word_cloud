[![Build Status](https://travis-ci.org/amueller/word_cloud.png)](https://travis-ci.org/amueller/word_cloud)
[![licence](http://img.shields.io/badge/licence-MIT-blue.svg?style=flat)](https://github.com/amueller/word_cloud/blob/master/LICENSE)

word_cloud
==========

A little word cloud generator in Python. Read more about it on the [blog
post][blog-post] or the [website][website]

## Installation

Fast install:

    pip install wordcloud

For a manual install get this package:
    
    wget https://github.com/amueller/word_cloud/archive/master.zip
    unzip master.zip
    rm master.zip
    cd word_cloud-master

Install the requirements:

    sudo pip install -r requirements.txt

Install the package:

    python setup.py install

Note that if you are not on Ubuntu, you need to pass a ``font_path`` to the WordCloud object ([docs](http://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud)) to point to
some existing font.


## Examples

Check out [examples/simple.py][simple] for a short intro. A sample output is:

![Constitution](examples/constitution.png)

Or run [examples/masked.py][masked] to see more options. A sample output is:

![Alice in Wonderland](examples/alice.png)

Getting fancy with some colors:
![Parrot with rainbow colors](examples/parrot.png)

## Used in

### Reddit Cloud

[Reddit Cloud][reddit-cloud] is a Reddit bot which generates word clouds for
comments in submissions and user histories. You can see it being operated on
[/u/WordCloudBot2][wc2] ([top posting][wc2top]).

![A Reddit Cloud sample](http://i.imgur.com/tcbZnKW.png)

### Chat Stats (Twitch.tv)

[Chat Stats][chat-stats] is a visualization program for Twitch streams,
which generates word clouds for comments made by Twitch users in the chat.
It also creates various charts and graphs pertaining to concurrent viewership
and chat rate over time.

![Chat Stats Sample](http://i.imgur.com/xBczk0x.png)

### Twitter Word Cloud Bot

[Twitter Word Cloud Bot][twitter-word-cloud-bot] is a twitter bot which generates
word clouds for twitter users when it is mentioned with a particular hashtag.
[Here][twitter-wordnuvola] you can see it in action, while [here][imgur-wordnuvola]
you can see all the word clouds generated so far.

### Winston Churchill speech "We Shall Fight on the Beaches" 
Pulled text from http://www.winstonchurchill.org/resources/speeches/128-we-shall-fight-on-thebeaches

![Winston Churchill speech](./notebooks/notebookoutput/churchill_speech.png)

### [other]

*Send a pull request to add yours here.*

## Issues

Using Pillow instead of PIL might might get you the [`TypeError: 'int' object is
not iterable` problem][intprob] also showcased on the blog.

[blog-post]: http://peekaboo-vision.blogspot.de/2012/11/a-wordcloud-in-python.html
[website]: http://amueller.github.io/word_cloud/
[simple]: examples/simple.py
[masked]: examples/masked.py
[reddit-cloud]: https://github.com/amueller/reddit-cloud
[wc2]: http://www.reddit.com/user/WordCloudBot2
[wc2top]: http://www.reddit.com/user/WordCloudBot2/?sort=top
[chat-stats]: https://github.com/popcorncolonel/Chat_stats
[twitter-word-cloud-bot]: https://github.com/defacto133/twitter-wordcloud-bot
[twitter-wordnuvola]: https://twitter.com/wordnuvola
[imgur-wordnuvola]: http://defacto133.imgur.com/all/
[intprob]: http://peekaboo-vision.blogspot.de/2012/11/a-wordcloud-in-python.html#bc_0_28B


## Licensing
The wordcloud library is MIT licenced, but contains DroidSansMono.ttf, a true type font by Google, that is apache licensed.
The font is by no means integral, and any other font can be used by setting the ``font_path`` variable when creating a ``WordCloud`` object.
