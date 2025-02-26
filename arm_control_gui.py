import lcm
from flask import Flask, request, jsonify
import arm_control  # Generated by lcm-gen from arm_control.lcm

app = Flask(__name__)
lc = lcm.LCM()

@app.route('/')
def index():
    # Return HTML directly without using an external template file
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>6-Axis Arm Control Panel</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .slider-container { margin-bottom: 20px; }
        .slider-label { display: inline-block; width: 120px; }
        button { margin-right: 10px; }
        input[type=range] { width: 300px; }
      </style>
    </head>
    <body>
      <h1>6-Axis Arm Control Panel (Live Update)</h1>
      <div>
        <div class="slider-container">
          <label class="slider-label" for="a1">A1 (Rotation):</label>
          <input type="range" id="a1" name="a1" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="a1_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label" for="a2">A2 (Pitch):</label>
          <input type="range" id="a2" name="a2" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="a2_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label" for="a3">A3 (Pitch):</label>
          <input type="range" id="a3" name="a3" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="a3_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label" for="a4">A4 (Roll):</label>
          <input type="range" id="a4" name="a4" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="a4_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label" for="a5">A5 (Pitch):</label>
          <input type="range" id="a5" name="a5" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="a5_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label" for="a6">A6 (Roll):</label>
          <input type="range" id="a6" name="a6" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="a6_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label" for="effector">Effector:</label>
          <input type="range" id="effector" name="effector" min="-10" max="10" step="0.1" value="0" oninput="updateAndSend()">
          <span id="effector_val">0</span>
        </div>
        <div class="slider-container">
          <label class="slider-label">A5-A6 Mode:</label>
          <input type="radio" name="a5a6_mode" id="mode_sync" value="sync" checked>
          <label for="mode_sync">Sync</label>
          <input type="radio" name="a5a6_mode" id="mode_antisync" value="antisync">
          <label for="mode_antisync">Opposite</label>
        </div>
        <button onclick="resetSliders()">Reset Axes</button>
      </div>
      <script>
        // Update displayed value and send control message live
        function updateAndSend() {
          var ids = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'effector'];
          var data = {};
          // Read slider values and apply a deadzone of 2 (i.e. values with abs < 2 become 0)
          ids.forEach(function(id) {
            var val = parseFloat(document.getElementById(id).value);
            document.getElementById(id + "_val").innerText = val;
            data[id] = (Math.abs(val) < 2) ? 0 : val;
          });
          
          // Get current mode for A5 and A6
          var mode = document.querySelector('input[name="a5a6_mode"]:checked').value;
          if (mode === "sync") {
            // In sync mode, let A5 control both: set A6 equal to A5.
            data['a6'] = data['a5'];
            document.getElementById('a6').value = document.getElementById('a5').value;
            document.getElementById('a6_val').innerText = document.getElementById('a5').value;
          } else {
            // In opposite mode, set A5 to be the negative of A6.
            data['a5'] = -data['a6'];
            document.getElementById('a5').value = -document.getElementById('a6').value;
            document.getElementById('a5_val').innerText = -document.getElementById('a6').value;
          }
          
          // Send the updated control message via POST
          fetch('/send_control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              a1: data.a1,
              a2: data.a2,
              a3: data.a3,
              a4: data.a4,
              a5: data.a5,
              a6: data.a6,
              effector: data.effector
            })
          })
          .then(response => response.json())
          .then(json => {
            console.log("Control message sent: ", json.control);
          })
          .catch(error => {
            console.error("Error:", error);
          });
        }

        // Reset axes A1-A6 (effector remains unchanged) and send update.
        function resetSliders() {
          var ids = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6'];
          ids.forEach(function(id) {
            document.getElementById(id).value = 0;
            document.getElementById(id + "_val").innerText = 0;
          });
          updateAndSend();
        }
      </script>
    </body>
    </html>
    """
    return html

@app.route('/send_control', methods=['POST'])
def send_control():
    data = request.get_json()
    a1 = float(data.get('a1', 0))
    a2 = float(data.get('a2', 0))
    a3 = float(data.get('a3', 0))
    a4 = float(data.get('a4', 0))
    a5 = float(data.get('a5', 0))
    a6 = float(data.get('a6', 0))
    effector = float(data.get('effector', 0))
    
    # Create and publish the LCM message with the control speeds.
    msg = arm_control.ArmControl()
    msg.a1 = a1
    msg.a2 = a2
    msg.a3 = a3
    msg.a4 = a4
    msg.a5 = a5
    msg.a6 = a6
    msg.effector = effector
    
    lc.publish("ARM_CONTROL", msg.encode())
    print("Published ARM_CONTROL message: ", [a1, a2, a3, a4, a5, a6, effector])
    return jsonify({"status": "sent", "control": [a1, a2, a3, a4, a5, a6, effector]})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
