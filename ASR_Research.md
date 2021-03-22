# ASR Research
### What is ASR?
**A**utomatic **S**peech **R**ecognition programs process human speech and convert it into text.
ASR programs record some speaker(s) and create an audio file of the speech it heard. The file can be cleaned and processed to reduce background noise, levle the volume, etc. The audio is then broken down and analyzed in sequences. The ASR software uses statistical probability to identify words, and then sentences. Human transcribers can improve the program's accuracy by correcting errors manually.  

Some problems that ASR systems face include non-static aspects of speech (eg. accents) and difficulty in collecting high-quality datasets. Background noise, in particular poses a significant obstacle in practical applications of speech recognition. Real-life conditions are often unknown prior to deployment, and are difficult to predict. For example, the hindrance of noise in a distant-microphone speech recognition system at a stadium, or on a metro platform, is varied and possibly massive.

#### Applications of ASR
- Live captions and transcriptions of media (usually adhering to FCC or other standards)
- Transcribing dictated notes (doctors in surgery, laboratory researchers, etc.)
- Aids for students/employees with non-standard needs (disabilities, non-native speakers, etc.)
- Court recording and other legal proceedings (digital transcription, scale)
- Many other practical applications in every field

##  
### Noise-Robust ASR
The goal of making automatic speech recognition technologies "noise robust" is to reduce the impact of mismatches between training and testing conditions. Since the statistics of background noise are difficult to predict, implementing noise reduction techniques should be done based on few (or none) assumptions about the noise. A noise robust technology should be insensitive to a wide range of noise disruptions. Implementing techniques to reduce noise can be done at the signal level, or the front-end or back-end of the ASR system. "Denoising" can introduce distortion and artifacts, which then reduce ASR accuracy. 

Often, signal processing requires domain expertise and/or simplifying assumptions. Success in noise robust improvements have been achieved by specifically engineering front-ends, or by training systems on specific high-volume datasets, but this is less effective when applied to wider areas. Reverberation also degrades the accuracy of ASR systems, especially in distant-microphone settings.
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
![GAN General Workflow](/images/gfg_gans-workflow.jpg)

#### GANs applied to Noise Reduction
Training ASR systems on text-to-speech (TTS) outputs is limited by a lack of acoustic diversity in TTS programs, and text corpuses are much larger than transcibed speech corpuses (so synthesizing all text data is unwieldy). GAN systems offer a way to increase acoustic diversity in synthesized speech data, which enables more sophisticated training of speech recognition systems. Applying GANs can enable a directly data-driven approach to encouraging robustness. The general goal of using GANs to improve noise robustness is training encoders to map noisy audio to the same embedding space as that of clean audio.
- One approach to improve ASR robustness is to reconstruct only those aspects of the audio which are important for predicting the text spoken and ignore everything else.  In terms of a GAN, the embedding of clean input audio is treated as real data and the embedding of noisy audio, which can either be augmented from the real or drawn from a different modality, as being fake. <sup>9</sup>  
- Regarding dereverberation: the generator tries to learn a transformation from reverberant speech to clean speech and the discriminator tries to determine whether the samples come from the generator or real-data. <sup>10</sup>

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
[9] https://deepai.org/publication/robust-speech-recognition-using-generative-adversarial-networks  
[10] https://arxiv.org/abs/1803.10132  
[11] https://towardsdatascience.com/understanding-generative-adversarial-networks-gans-cd6e4651a29  
