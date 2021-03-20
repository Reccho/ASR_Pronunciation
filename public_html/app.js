$(document).ready(function () {
//methods
	
	function selectPhrase() {
		$('phrase').val('');
		
		max_val = 0;
		//REQUEST: Total number of phrases in xml document
		$.ajax({ //Get total number of phrases in xml library file
			type: "POST",
			data: {
				action: "numPhrase", 				// Will forward to getPhrase()
			},
			url: "http://localhost:5000/Action",
			
			success: result => {
				//max_val = result;
				console.log(result);
			},
		});

		//Check if phrase # is out of bounds and reset accordingly

		//REQUEST: Fetch phrase text form xml, search by 'id'
		$.ajax({ // Post-Request: Get Phrase from xml file by id and display text string 
			type: "POST",
			data: {
				action: "getPhrase", 				// Will forward to getPhrase()
				idDataset: $('#dataset').val(), 	// Pass value of "Dataset"
				idPhrase: $('#phraseNumber').val()	// Pass value of "Phrase number"
			},
			url: "http://localhost:5000/Action",
			
			success: result => {
				//$('#phrase').empty().append(result); // Display new phrase to user
				console.log(result);
			},
		});
	}
	
	$(document).on("input", "#phraseNumber", selectPhrase);

	//main
	if (navigator.mediaDevices) {
		var audio = { audio: true };
		var chunks = [];
		var blob = null;
		var clipName = "";

		navigator.mediaDevices.getUserMedia(audio).then(function (stream) {
				var mediaRecorder = new MediaRecorder(stream);	// Init

				// On-Click: "Record"
				$("#record").click(function () {
					$("#playback").trigger("stop");	// Stop playing preview
					chunks = [];					// Set chunks empty
					mediaRecorder.start();			// Start recording

					//Button updates
					$("#stop").attr("disabled", false);			//enable
					$("#grade").attr("disabled", true);			//disable
					$("#record").attr("disabled", true);		//disable
				});

				// On-Click: "Stop"
				$("#stop").click(function () {
					mediaRecorder.stop();	// Stop recording

					//Button updates
					$("#record").attr("disabled", false);		//enable
					$("#grade").attr("disabled", false);		//enable
					$("#stop").attr("disabled", true);			//disable
				});

				// On-Click: "Grade"
				$("#grade").click(function() {
					score = 0;
					//REQUEST: Pass audio to grading function and get score value (decimal)
				});

				mediaRecorder.onstop = function (e) {
					clipName = $("#dataset").val() + "_" + $("#phraseNumber").val();
					blob = new Blob(chunks, { 'type': 'audio/ogg; codecs=opus' });
					chunks = [];
					var audioURL = URL.createObjectURL(blob);
					$("#preview").attr("src", audioURL);

					if ($("#autoplay").is(":checked"))
						$("#preview").trigger("play");
				}

				mediaRecorder.ondataavailable = function (e) {
					chunks.push(e.data);
				}

			})
			.catch(function (err) {
				alert('Error encountered: ' + err);
			})
	}
});
