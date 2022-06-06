# Building reposnoop

**reposnoop** is a project I had in mind for a while. I wanted to analyze GitHub
repos relevant to a particular topic in a bit more depth without having to 
click through them on foot.

> If you use it more than three times, automate it.

Now I attend a Python course and need to do my final assignment. So what could be 
more obvious than to make reposnoop my project?

## Getting started

We want to pull data from GitHub, which has a pretty good
[API](https://docs.github.com/en/rest), full-featured with
tons of instructions, examples and detailed references. We need to collect
this data in a way easy-to-handle, review and save it. We'd like as well to 
read it back from disk for further analysis. After all, GitHub API (like any other)
is rate limited.

We'd like to see some graphical presentation of data and analysis. And we'd like to 
handle all of this by a GUI.

Hence, the project divides into:
* building an API client (including caching and rate management)
* defining the data management infrastructure
* develop tools for analysis and charting
* wrap a nice GUI around it for easy interaction

First things first: If we have no data, all of the other steps make no sense. 
So we start over with the API client part, to get some real GitHub data. From 
this we learn early what we will be dealing with further on.

### The GitHub API
The GitHub REST API is pretty well documented, we find it here: 
[https://docs.github.com/en/rest](https://docs.github.com/en/rest)

We issue a simple request by curl, and we get:

    > curl https://api.github.com/zen
    
    StatusCode        : 200
    StatusDescription : OK
    Content           : Approachable is better than simple.
    
Nice. That was easy. Now we take a quick look at what is currently
[trending Python](https://github.com/trending/python?since=daily) 
at GitHub, and choose one of the first to take a deeper look via API:

    > curl https://api.github.com/users/pittcsc
    
    StatusCode        : 200
    StatusDescription : OK
    Content           : {"login":"pittcsc","id":7276234,"node_id":"MDEyOk9yZ2FuaXphdGlvbjcyNzYyMzQ=","avatar_url":"https://avatars.g 
                        ithubusercontent.com/u/7276234?v=4","gravatar_id":"","url":"https://api.github.com/users/pit...
    RawContent        : HTTP/1.1 200 OK
                        Vary: Accept, Accept-Encoding, Accept, X-Requested-With
                        X-GitHub-Media-Type: github.v3; format=json
                        Access-Control-Expose-Headers: ETag, Link, Location, Retry-After, X-GitHub-OTP, X...
    Headers           : {[Vary, Accept, Accept-Encoding, Accept, X-Requested-With], [X-GitHub-Media-Type, github.v3; format=json],
                        [Access-Control-Expose-Headers, ETag, Link, Location, Retry-After, X-GitHub-OTP, X-RateLimit-Limit,
                        X-RateLimit-Remaining, X-RateLimit-Used, X-RateLimit-Resource, X-RateLimit-Reset, X-OAuth-Scopes,
                        X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type, X-GitHub-SSO, X-GitHub-Request-Id,
                        Deprecation, Sunset], [Access-Control-Allow-Origin, *]...}
    Images            : {}
    InputFields       : {}
    Links             : {}
    ParsedHtml        : mshtml.HTMLDocumentClass
    RawContentLength  : 1333

The __Content__ portion of it looks like some JSON. We already get

    "login": "pittcsc"
    "id": 7276234
    "node_id": "MDEyOk9yZ2FuaXphdGlvbjcyNzYyMzQ="
    "avatar_url": "https://avatars.githubusercontent.com/u/7276234?v=4"
    "gravatar_id": ""

while not even logged in yet. But wait - didn't we plan to walk the short way? We do not need 
to invent the wheel a second time. There are already
[Python wrapper libs](https://docs.github.com/en/rest/overview/libraries#python) for GitHub API.
So we use one of these. The most starred ones are
* [PyGitHub](https://github.com/PyGithub/PyGithub), and
* [github3](https://github.com/sigmavirus24/github3.py)

They look both well maintained from first impression. For the time being we stick to
PyGitHub. This is not a decision based on a thorough analysis and comparison - we'd just like 
to go on and decide for the bigger one (in terms of contributors, stars, forks, ...) 
of two libs with much recent activity and many stars.

We install with:

    python -m pip install PyGithub

Now we're set. Let's give it a try:

from github import Github as gh











<br/>

### Work in progress

By now this project is under heavy construction. Everything you see here might be non-functional
or contain code or ressources that are not intended to stay here.

<br/>
<br/>
<br/>
<br/>

***

### Here comes only copy-paste boilerplate text.

<br/>

> A place to copy-paste your README.md from

One of the most crucial things in your open source project is the `README.md`
file. This repository has a ready-to-copy-paste template you can use for all
your projects.

## Getting started

Copy the `README-default.md` file for yourself and start editing! At the root of
your project, run:

```shell
curl https://raw.githubusercontent.com/jehna/readme-best-practices/master/README-default.md > README.md
```

The code above fetches the `README-default.md` file from this repository.
Here you should say what actually happens when you execute the code above.

### Initial Configuration

Some projects require initial configuration. How to start the prog:

```shell
atom README.md
```

And again you'd need to tell what the previous code actually does.

## Features

What's all the bells and whistles this project can perform?
* What's the main functionality
* You can also do another thing
* If you get really randy, you can even do this

## Configuration

Here you should write what are all of the configurations a user can enter when
using the project.

## Ressources

Which ressources are used, e.g. libs, APIs ...

#### Argument 1
Type: `String`  
Default: `'default value'`

State what an argument does and how you can use it. If needed, you can provide
an example below.

Example:
```bash
awesome-project "Some other value"  # Prints "You're nailing this readme!"
```

#### Argument 2
Type: `Number|Boolean`  
Default: 100



```shell
git add README.md
git commit -m "Added: README"
git push
```


E.g. if you have a perfect `README.md` for a Grunt project, just name it as
`README-grunt.md`.

## Related projects

Here's a list of other related projects where you can find inspiration for
creating the best possible README for your own project:

- [Billie Thompson's README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
- [A list of awesome READMEs](https://github.com/matiassingers/awesome-readme)
- [Akash Nimare's kickass README guide](https://gist.github.com/akashnimare/7b065c12d9750578de8e705fb4771d2f)
- [Dan Bader's README template](https://github.com/dbader/readme-template)

## System requirements

here some screenshots ...

## Screenshots

here some screenshots ...

## Licensing

This project is licensed under MIT license.

View [LICENSE](LICENSE).

[issues]:https://github.com/jehna/readme-best-practices/issues/new

> How to paste blockquotes.

Tables work, too.
Colons can be used to align columns.

| Tables        | Are           | Cool  |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | $1600 |
| col 2 is      | centered      |   $12 |
| zebra stripes | are neat      |    $1 |

There must be at least 3 dashes separating each header cell.
The outer pipes (|) are optional, and you don't need to make the 
raw Markdown line up prettily. You can also use inline Markdown.

    Markdown | Less | Pretty
    --- | --- | ---
    *Still* | `renders` | **nicely**
    1 | 2 | 3


some kind of `strikethrough.txt` for file names

run stuff in shell (command line):

```shell
curl https://raw.githubusercontent.com/jehna/readme-best-practices/master/README-default.md > README.md
```

## Starting over: First week.
Here are
some of the tasks:

<details>
    <summary>Example #1 (click!)</summary>

        source code
        source code
        source code

</details>

Easily make a list:
* just put stars at
* the beginning of the line
* and it will magically format itself

<br/>

Interpreter for [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) programs.

https://github.com/matiassingers/awesome-readme
