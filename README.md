As a part of my Computer Engineering degree course, My team and I were tasked with creating a project completely from scratch. 
Creating an automatic transistor characterizer was what we decided on due to its applicable use within the university. 
This code is ran on a Raspberry Pi 2 Model B with raspbian OS.
This code connects to an arduino via serial communication from which it recieves all the data being sent over.
From there, the code will create a database, if one has no already been made, and will parse the information and save it into the database incase the user wanted to refer back to previous experiments.
Once the information was stored, using MATPLOTLIB, we were able to generate the graphs of VGS vs  Current and VGS vs. sqrt(ID).
Also using the scipystats library, we were able to calculate the Kn and Vt values of the transistor we were testing.
Main Author: Caleb Garza
Co-Authors: Laura Leal, Jose Amaro
