# What is OVERPRINT?

OVERPRINT is a colour helper for printing posters.

Imagine you designed a poster with eight colours. Some are very similar: two oranges, two blues, two yellows and two dark shades. OVERPRINT tries using one printing ink for each similar pair. In our example, that means four inks instead of eight.

It then shows you what the poster could look like. You decide whether you like the changes.

## The three things you do

1. **Choose your colours.** Try the example or click the colour squares to change them.
2. **Compare before and after.** Move the slider to allow less or more colour change, then click Find my ink plan.
3. **Save a result you like.** Check the colours that changed most, then save the poster or your settings.

The site currently recolours the sample poster. It does not extract colours from any uploaded photograph or artwork. A real print can look different from a screen, so check a test print before production.

## What the words mean

- **Ink:** a colour used in printing.
- **Palette:** your collection of colours.
- **Preview:** a picture showing a possible result before you commit to it.
- **Colour change:** how different a suggested colour is from the original.
- **Algorithm:** a set of steps the computer follows to solve a problem.
- **Data structure:** a way the computer organizes information so it can work with it.

## What the computer does

First, it checks which printing inks look close enough to your original colours. Then it suggests an ink combination. Finally, it points out the colours that changed most, so you know which ones to check carefully.

You can explain the whole project like this:

> “My project helps a designer try fewer printing inks. It combines similar colours, shows a before-and-after preview, and highlights the biggest changes. The designer decides whether the result still looks good.”

## Only when you are ready for the names

- **Set cover** chooses a useful combination of inks.
- **Quickselect / Median of Medians** find the colour changes most worth checking.
- **Max-heap** puts the largest change first in that list.

These names describe the computer's internal steps. Start by understanding the colour problem and the before/after result; the detailed methods can come next.
