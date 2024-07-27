## Author Info
Name: Rishi Rajendran  
E-mail: rr247@duke.edu  

## Program Use
In order to use this program, change the ```file_name``` variable in the ```main()``` 
function of the program to the specific .txt file with the data you wish to analyze.
Afterwards, to run the program, enter ```python cpap.py``` into your terminal window.  

## Breath Detection Algorithm
In order to detect breaths in the flow data, first the indices of all the local 
maxima were found using Python's ```scipy``` package. Then, the flow values between
each of these peaks were analyzed for zero-crossings or negative values. Any index
referencing a peak that was followed by a return to zero or a negative value before 
the next peak was stored in a separate list. This separate list contained the final 
indices of the flow list where breaths occurred.  

## Software License
MIT License

Copyright (c) [2024] [Rishi Rajendran]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

