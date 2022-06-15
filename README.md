# Stegoimage
To use the script in encoding mode use:
    python stegoimage_script.py --encode [text or path_to_text] [path_to_source_img] [path_to_embedded_img]

To use the script in decode mode use:
    python stegoimage_script.py --decode [path_to_embedded_img]

To use the script in compare mode use:
    python stegoimage_script.py - [path_to_original_img] [path_to_embedded_img] [path_to_comparative_img]

In any case, the images used to execute the commands must have a .png extension
If the image you want to use to embed the text has width (w) and length (h), the maximun number of
embeddable characters (n) is given by the expression: n = w x h - c, where c = 17
(Note: c is the number of pixels occupied by the information needed to decode the image).

Short description of the "step", that is the way in which the single characters of the input text are incorporated inside
Image:
The characters to embed are distributed equally over the whole image by calculating the "step".
The "step" has value: s = (w * h - 17) // t ; where t = number of characters of the input text.
Each pixel, starting from the coordinates (0,17) of the image matrix, is written every s positions in the matrix.

--------------------------------------------------------------------------------------------------------------------------
For info and suggestions contact me here: 78switching91@protonmail.com
