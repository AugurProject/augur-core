### so the things you need for learning serpent aka background knowledge is as follows
a string is this: `"faffafwf"`

this is also a string: `"roflcopter"`

so is `"A"`

an array is this: `["what", "lol", "banana", "orange", "fish"]`

an array is also `["blam", "fuck"]`

`[1, 2, 44, 47, 22, 9424, 2]` is also an array

in some programming languages (including serpent) an array is also:

    [1, "fish", "banana", 3, 4, 5, "fish"]

now there are these things called variables, which is really basic, all it means is..

i can say

    x = 47

and then if i do `x*2` i'll get `96`

so i can also do

    x = "i love asana"

or i can even say

    myFavoriteGames = array(3)

### and here we're going to do something a bit weird

now i'm going to do

    myFavoriteGames[0] = "halo"
    myFavoriteGames[1] = "halo"
    myFavoriteGames[2] = "halo"

notice that all 3 of my favorite games are halo

and that we created an array with length 3

the `array(3)` concept is known as a constructor

it "constructs" something, and we give that constructor a thing called a parameter, the parameter in this case is the number 3

but notice, there is `myFavoriteGames` 0, 1, and 2, there is no `myFavoriteGames[3]`

this is because arrays and most things in computer science are "indexed" starting at 0, aka they start at 0, not 1

computer scientists count from 0 up, not 1 up

when we do `myFavoriteGames[0] = "halo"` we are saying, take the 0th / zeroth item in the array `myFavoriteGames` and set it to "halo"

if we wanted to print out all of the contents of `myFavoriteGames`

we would see `["halo", "halo", "halo"]`

in certain special cases which you'll come across when vitalik talks about "data" we can "initialize"/create an array using a different "syntax" or style

in this scenario it may be appropriate to create an array like this:

    data myFavoriteGames[]

this creates an array with no specified length, also known as a "lazy array" - my favorite!
now we can do things like

    myFavoriteGames[0] = "final fantasy"

or, with Serpent (this isn't the case for most programming languages)
we can do fancy things like:

    myFavoriteGames["fantasy genre"] = "final fantasy"

now here's where really fancy fun stuff starts to occur, we can do:

    data myFavoriteGameGenres[](games[](name))

wow! that looks like a clusterfuck mess

welcome to programming :)

so we're about 70% done with what you need to know to be able to understand the vitalik post enough to play with it and ask questions

i recommend rereading this a few times, trying out actually typing it -- sounds stupid, trust me, type it and you will remember it better

just open this in one tab, type in a word processor like sublime text in another
google `sublime text`

open it, go to bottom right corner and click `python -> python`

### now let's dissect this clusterfuck

so we're learning the concept of multdimensional arrays right now -- woohoo! sounds fancy right! (not really)

so we were back at the clusterfuck

`data myFavoriteGameGenres[]` is an array of game genres

you can imagine `myFavoriteGameGenres["shooters"]` or `myFavoriteGameGenres["fantasy"]`

now there can be another array located within one of the indexes of that array

    myFavoriteGameGenres["fantasy"].games[]

that designates all the games within the fantasy genre

    myFavoriteGameGenres["fantasy"].games[0].name = "halo"

0 designates that it's the zeroth game

the name is halo

    myFavoriteGameGenres["fantasy"].games[1].name = "call of duty"

the 1st game in the list is named call of duty

ok final topic to cover

### functions and definitions

a function is just what it sounds like - same as math - you have a thing that you give some inputs to and it does shit

here's an example of how serpent does it:

    def get_money():
        # do things to get money 
        # is a comment

then you can do things like `get_money()`

and it will get money

you can also do things like

    def get_money(currency):

and then the body of that function will be

    if(currency=="bitcoin"):
        return(1)
    elif(currency=="usd"): 
        return(0)

then i can say

    x = get_money("bitcoin")

and `x` will now equal `1`

(`elif` means else followed by if)
