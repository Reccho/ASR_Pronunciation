$(document).ready(function () {
    var PAGE = window.location.href;
    console.log(PAGE);                              //debug
    LocalHost = ''                                  // '' or http://localhost:5000
    const id = Date.now().toString()                // create "uuid" from timestamp
    max_val = 1;                                    // default value
    $("#spectrogram").hide();                       // toggle: hide/show
    $('#phraseNumber').val(0);                      // begin number field at 0
    $('#phrase').empty().append("Hello, World.");   // default phrase
    $("#grade").attr("disabled", true);		        // disable on load
    $("#playback").attr("disabled", true);          // disable playback on page load
    req_getDatasets(); // Begin by loading available phrase libraries (populate $Dataset)


    //Request Functions
    function req_getPhrase() {
        $.ajax({ // Post-Request: Get Phrase from xml file by id and display text string 
            url: (LocalHost + "/Library"),
			type: "POST",
			data: {
				action: "getPhrase", 	                            // Will forward to getPhrase()
				idDataset: $('#dataset option:selected').text(), 	// Pass value of "Dataset"
				idPhrase: $('#phraseNumber').val()	                // Pass value of "Phrase number"
			},
			
			success: function(data) {
				$('#phrase').empty().append(data);  // Display new phrase to user
                $('#score').empty();                // Clear old score/"you said" text
                $('#spectrogram').hide();           // toggle off
				$("#grade").attr("disabled", true); // turn button off
                $("#playback").attr("src", '');     // clear playback 
                console.log(data);                  //debug
			},
		});
    }

    function req_numPhrase() {
		$.ajax({ //Get total number of phrases in xml library file
            url: (LocalHost + "/Library"),
			type: "POST",
			data: {
				action: "numPhrase", 				                // Will forward to numPhrase()
                idDataset: $('#dataset option:selected').text(), 	// Pass value of "Dataset"
			},
			
			success: function(data) {
                max_val = parseInt(data);
			},
		});
    }

    function req_getDatasets() {
        $.ajax({ //Get total number of phrases in xml library file
            url: (LocalHost + "/Library"),
			type: "POST",
			data: {
				action: "getDatasets", 	// Will forward to getDatasets()
			},
			
			success: function(data) {
                var files = data.split(' '); // split string on space

                files.forEach((element, index) => {
                    let option = document.createElement('option');
                    option.value = index;          // Add index to option
                    option.textContent = element;  // Add element HTML
                    $('#dataset').append(option);  // Append option to Dataset (select)
                  });

                console.log("Datasets available: ", files);     //debug
                console.log("DateTime-id: " + id);              //debug
			},
		});
    }

    window.onbeforeunload = function (e) {
        e = e || window.event;
        $.ajax({ //Get total number of phrases in xml library file
            url: (LocalHost + "/Clear"),
            type: "POST",
            data: { uuid: id },
            
            success: function(data) {
                resolve(data);
                console.log(data);      //debug
            },
        });
    }

    //Utility Functions
    function selectPhrase() {
        req_numPhrase();    //Get the total number of phrases in the file

		//Check if phrase # is out of bounds and loop accordingly
        p_num = parseInt($('#phraseNumber').val());
		if (p_num > max_val) {
            $('#phraseNumber').val(1);
		} else if (p_num < 1) {
            $('#phraseNumber').val(max_val);
		}

		req_getPhrase(); // Get the actual text of the phrase selected
	}

    function refreshSpectro(){    
        var img = document.getElementById("spectrogram");
        var timestamp = new Date().getTime();   // create a new timestamp 
        var queryStr = "?t=" + timestamp;    // add to image filename

        img.src = "/home/nichols/sw_project/temp/spectro.png" + queryStr;     // "?t--" is discarded
        $('#spectrogram').attr('src', "/home/nichols/sw_project/temp/spectro.png" + new Date().getTime());
    }

    //On-Input functions
    $(document).on("input", "#phraseNumber", selectPhrase);

    $(document).on("input", "#dataset", function() {
        $('#phraseNumber').val(0);                      // begin number field at 0
        $('#phrase').empty().append("Hello, World.");   // default prompt
        max_val = 1;                                    // default value
        selectPhrase();
        console.log("New phrase library selected.");    ////debug
    });

    
    //"main"
    if (navigator.mediaDevices) {
        var audioConstraint = { audio: true };
        var audioBlob = null;
        var clipName = "";
        var chunks = [];

        navigator.mediaDevices.getUserMedia(audioConstraint).then(function (stream) {
                var mediaRecorder = new MediaRecorder(stream);	// Init

                // On-Click: "Record"
                $("body").on('click', '#record', function () {
                    console.log("'Record' clicked.");
                    $("#playback").trigger("stop");	// Stop playing preview
                    chunks = [];					// Set chunks empty
                    mediaRecorder.start();			// Start recording

                    //Element updates
                    $("#spectrogram").hide();                   // toggle: hide/show
                    $("#stop").attr("disabled", false);			//enable
                    $("#grade").attr("disabled", true);			//disable
                    $("#record").attr("disabled", true);		//disable
                    $("#playback").attr("disabled", true);      // disable
                    $('#score').empty(); // Clear old score/"Recognized: " text
                });

                // On-Click: "Stop"
                $("#stop").click(function () {
                    mediaRecorder.stop();	// Stop recording
                    $.ajax({ //REQUEST: Store the text prompt in 'sample.txt'
                        url: (LocalHost + "/Store_Phrase"),
                        type: "POST",
                        data: {
                            text: $("#phrase").text(), 
                            uuid: id 
                        },
                        
                        success: function(data) {
                            console.log(data);     //debug
                        }
                    });

                    //Button updates
                    $("#playback").attr("disabled", false);      //enable
                    $("#record").attr("disabled", false);		//enable
                    $("#grade").attr("disabled", false);		//enable
                    $("#stop").attr("disabled", true);			//disable
                });

                // On-Click: "Grade"
				$("#grade").click(function() {
					$.ajax({ //REQUEST: Pass audio to grading function and get score value (decimal)
                        url: (LocalHost + "/Grade"),
                        type: "POST",
                        data: { uuid: id },
						
						success: function(data) {
                            if (data != "###") {    // If file is NOT the error value
                                var grade = data.split('\n');
                                $('#score').empty().append('Recognized: \"' + grade[0] + '\"');
                                $('#score').append('<br />' );
                                $('#score').append('Reference: [' + grade[2] + ']');
                                $('#score').append('<br />' );
                                $('#score').append('Correctness: ' + grade[4] + '%');
                                console.log(grade);     //debug
                            } else {
                                $('#score').empty().append("Your speech is still being graded. Press 'Grade' again in a few ms :)");
                                console.log("File does not exist or has wrong format.");     //debug
                            }
						}
					});
				});

                mediaRecorder.onstop = function (e) {   //Runs when mediaRecorder finishes
                    clipName = $("#dataset").val() + "_" + $("#phraseNumber").val();
                    audioBlob = new Blob(chunks, { 'type': 'audio/webm; codecs=opus' });
                    chunks = [];
                    var audioURL = URL.createObjectURL(audioBlob);
                    $("#playback").attr("src", audioURL);

                    if ($("#autoplay").is(":checked"))
                        $("#playback").trigger("play");
                    
                    let formData = new FormData();                              //create FormData holder
                    formData.append("uuid", id);                                //append uuid
                    formData.append("audio", audioBlob, "input_audio.webm");    //append audio Blob

                    console.log("here is the formdata...");     //debug
                    for (var pair of formData.entries()) {      //debug
                        console.log(pair[0]+ ', ' + pair[1]);   //debug
                    }

                    $.ajax({ //REQUEST: Pass audio to grading function and get score value (decimal)
                        url: (LocalHost + "/Store_Audio"),
                        type: "POST",
                        contentType: false,
                        processData: false,
                        enctype:"multipart/form-data",
                        data: formData,

                        success: function(result) {
                            $('#spectrogram').attr('src', 'data:image/gif;base64,' + result);
                            $("#spectrogram").show();   // toggle: hide/show
                        }
                    });
                }

                mediaRecorder.ondataavailable = function (e) {
                    chunks.push(e.data);
                    console.log("New recording: ", e.data);
                }

            })
            .catch(function (err) {
                alert('Error encountered: ' + err);
                console.log("Unable to access mic, probably...");
            })
    }
});
