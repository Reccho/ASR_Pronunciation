# ASR Research
### What is ASR?
**A**utomatic **S**peech **R**ecognition programs process human speech and convert it into text.
ASR programs record some speaker(s) and create an audio file of the speech it heard. The file can be cleaned and processed to reduce background noise, levle the volume, etc. The audio is then broken down and analyzed in sequences. The ASR software uses statistical probability to identify words, and then sentences. Human transcribers can improve the program's accuracy by correcting errors manually.  

#### Applications of ASR
- Live captions and transcriptions of media (usually adhering to FCC or other standards)
- Transcribing dictated notes (doctors in surgery, laboratory researchers, etc.)
- Aids for students/employees with non-standard needs (disabilities, non-native speakers, etc.)
- Court recording and other legal proceedings (digital transcription, scale)
- Many other practical applications in every field

##  
### Noise-Robust ASR
The goal of making automatic speech recognition technologies "noise robust" is to reduce the impact of mismatches between training and testing conditions. Since the statistics of background noise are difficult to predict, implementing noise reduction techniques should be done based on few (or none) assumptions about the noise. A noise robust technology should be insensitive to a wide range of noise disruptions. Implementing techniques to reduce noise can be done at the signal level, or the front-end or back-end of the ASR system. "Denoising" can introduce distortion and artifacts, which then reduce ASR accuracy. 
#### Some Noise Reduction Methods
- Remove harmonic spectral peaks from the voice, and use the residual signal to estimate background noise spectrum, which is then used to suppress the noise. Relies on the fundamental frequency of pitch in all human speech and its corresponding spectral harmonics.<sup>2</sup>
- Separate target speaker's voice from background sources based on non-negative matrix factorization (NMF) using variational Bayesian (VB) inference to estimate NMF parameters. <sup>3</sup>
- Suppress sound signals not arriving from a desired direction based on a time-varying minimum variance distortionless response (MVDR) beamformer that uses spatial information. <sup>3</sup>
- First, use a parametric model of acoustic distortion to estimate the clean speech and noise spectra in a principled way (eliminates need for manual heurisitc parameters). Then, apply a Wiener filter to further reduce noise while preserving speech spectra. <sup>4</sup>
- Use the time-activation matrices from convolutive non-negative matrix factorization (CNMF) as acoustic models to create speech and noise dictionaries that generate noise-robust time-activation matrices from noisy speech. <sup>5</sup>
- *Missing data approach:* Assumes some spectral-temporal regions will remain uncorrupted when speech is one of several sound sources. These regions can be used as ‘reliable evidence’ for recognition. <sup>6</sup>

##  
### Generative Adversarial Networks (GANs)
GANs are a class of neural network used for *unsupervised learning.* Basically, two neural networks are implemented: a **generator** and a **discriminator**. The generator creates samples of a type of data (images, audio, etc.). The discriminator distinguishes between the generated "fake" samples and real samples. Through this adversarial system the generator learns to make better samples and the discriminator becomes better at discerning fake vs real samples. The generator is trained in order to maximise the probability of the discriminator making a mistake and the discriminator is based on a model that estimates the probability that the sample that it got is received from the training data and not from the generator.  
[![GAN General Workflow](GeeksforGeeks "GAN General Workflow")](http://https://media.geeksforgeeks.org/wp-content/uploads/gans_gfg.jpg "GAN General Workflow")

#### GANs applied to Noise Reduction

##  
### Sources
[1] https://tinyurl.com/Verbit-AI  
[2] https://sail.usc.edu/publications/files/ROBFRONT_MVS.pdf  
[3] https://tinyurl.com/Multi-Channel-Enhancement  
[4] https://tinyurl.com/2-Stage-Wiener-Filtering  
[5] https://sail.usc.edu/publications/files/Vaz_2016_CNMF_robust.pdf  
[6] https://www.isca-speech.org/archive/archive_papers/eurospeech_2001/e01_0213.pdf  
[7] https://www.geeksforgeeks.org/generative-adversarial-network-gan/  
[8] http://www.interspeech2020.org/uploadfile/pdf/Mon-2-2-4.pdf
