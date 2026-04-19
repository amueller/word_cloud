# Estedad
![sample](https://github.com/aminabedi68/Estedad/blob/master/documentation/Estedad-sample.png)
Estedad(`/~este~dAd/` means Talent in persian) is an Arabic-Latin Sans-Serif typeface in 9 standard weights and a variable version(`wght`:weight/`KSHD`:Arabic simple kashida). Estedad has wide codepoint range support for most Arabic and Latin languages.
<br>design of type is simple, smooth, compact, legible, low contrast, lowest optical size(a bit higher in bold and above weights) and optimized for web-like environments.
<br>Estadad supporting small caps, simple fractions, tabular and old-style numbers and both decomposed(limited to basic a-z A-Z letters) and precomposed letter forms for Latin, and semi-advanced quran marking methodes for Arabic script.
<br>this typeface designed inside fontforge(in two thin and black masters). variable font and static instances build with fontmake and help of python scripts(fontforge python api and fonttools). whole project is licenced to be free under open font licence v1.1.
<br>quality of variable font has improved under fontbakery advisments.

## Weights and Axes
Estedad has 9 Weights(Standard weights, 100-Thin to 900-Black) and 2 Axes(Weight[wght]:100-900 // Kashida[KSHD]:100-200)

## Build(Windows):
### requirements:
1-installed <a href="https://github.com/fontforge/fontforge">fontforge</a> with path access in environment variables
<br>2-installed <a href="https://www.python.org/">python</a> and <a href="https://github.com/googlefonts/fontmake">fontmake</a>
### build:
move script folder contents to sources folder and run Build.bat
<br>(FD version of variable font created manually.)
<br>
<br>
![designspace](https://github.com/aminabedi68/Estedad/blob/master/documentation/Estedad-designspace.png)

## weight axis nonlinearity:
The weight axis has a nonlinearity mapping to decrease distance of the bottom and increase distance of the above instances.
