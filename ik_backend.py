import lcm
from flask import Flask, request, jsonify
import target_position  # Generated by lcm-gen from target_position.lcm

app = Flask(__name__)
lc = lcm.LCM()

@app.route('/')
def index():
    html = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
         <meta charset="UTF-8">
         <title>Target Control Panel (Live Update)</title>
         <style>
           body { font-family: Arial, sans-serif; margin: 20px; }
           .slider-container { margin-bottom: 15px; }
         </style>
      </head>
      <body>
         <h1>Target Control Panel (Live Update)</h1>
         <div class="slider-container">
            <label for="x">X:</label>
            <input type="range" id="x" name="x" min="-0.5" max="0.5" step="0.01" value="0" oninput="updateAndSend()">
            <span id="x_val">0</span>
         </div>
         <div class="slider-container">
            <label for="y">Y:</label>
            <input type="range" id="y" name="y" min="-0.5" max="0.5" step="0.01" value="0" oninput="updateAndSend()">
            <span id="y_val">0</span>
         </div>
         <div class="slider-container">
            <label for="z">Z:</label>
            <input type="range" id="z" name="z" min="-0.5" max="0.5" step="0.01" value="0" oninput="updateAndSend()">
            <span id="z_val">0</span>
         </div>
         <script>
            function updateAndSend() {
               // Update displayed values
               var x = parseFloat(document.getElementById("x").value);
               var y = parseFloat(document.getElementById("y").value);
               var z = parseFloat(document.getElementById("z").value);
               document.getElementById("x_val").innerText = x;
               document.getElementById("y_val").innerText = y;
               document.getElementById("z_val").innerText = z;
               
               // Create data object
               var data = { x: x, y: y, z: z };
               // Send data via fetch to the backend
               fetch('/send_target', {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify(data)
               })
               .then(response => response.json())
               .then(json => {
                  console.log("Target sent: ", json.target);
               })
               .catch(error => {
                  console.error("Error:", error);
               });
            }
         </script>
      </body>
    </html>
    """
    return html

@app.route('/send_target', methods=['POST'])
def send_target():
    data = request.get_json()
    x = float(data.get("x", 0))
    y = float(data.get("y", 0))
    z = float(data.get("z", 0))
    # Create and publish an LCM message with the target position.
    msg = target_position.TargetPosition()
    msg.x = x
    msg.y = y
    msg.z = z
    lc.publish("TARGET_POSITION", msg.encode())
    print("Published LCM message with target: ", [x, y, z])
    return jsonify({"status": "sent", "target": [x, y, z]})

if __name__ == '__main__':
    app.run(debug=True, port=5003)
