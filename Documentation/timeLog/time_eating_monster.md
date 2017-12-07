My Savior: StackOverflow

## pyAudio
**1. OS error overflow**  
change the chunk size (sampling rate)  
**2. Module Matplotlib/pyaudio not found**  
change shell configuration, make sure you are in the correct env with correct python version  
**3. Matplotlib cannot dymanically graph**    
set output = False and scale x_lim and y_lim
**4. argmax() always return 0**
The first 20 ydata should be ignored as it is discontinuous 


## gcloud
**1. "command "gcloud" not found"**  
add the path (the one inside /bin) to bash profile  
**2. cannot Deploy**  
add app.yaml file to configure the deployment  

## mis
**1. cannot slice Nonetype**
Try not to return None for special case, return something that is the sametype as regular output. E.g. if regular output is digit, for special case return 0.
**2. matplotlib welcome screen**
Matplotlib widgets and animation turns out to be very difficult to use and not 
very customizable. I'm considering moving the entire program to tk backend. 
