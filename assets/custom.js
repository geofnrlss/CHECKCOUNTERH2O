window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        play_beep: function(moisture_text) {
            if (!moisture_text) return "";

            // Ambil angka dari teks (misal "1.80 %" jadi 1.80)
            var val = parseFloat(moisture_text.replace(/[^\d.-]/g, ''));
            
            if (val > 1.5) {
                var context = new (window.AudioContext || window.webkitAudioContext)();
                var osc = context.createOscillator();
                var gain = context.createGain();
                
                osc.type = "sine";
                osc.frequency.value = 1000; 
                osc.connect(gain);
                gain.connect(context.destination);
                
                osc.start();
                setTimeout(function() { 
                    osc.stop(); 
                    context.close();
                }, 200);
            }
            return "Sound Played";
        }
    }
});