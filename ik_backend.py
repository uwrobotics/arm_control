import lcm
from flask import Flask, request, jsonify
import target_position  # Generated by lcm-gen from target_position.lcm

app = Flask(__name__)
lc = lcm.LCM()

@app.route('/')
def index():
    # Return HTML directly without using a template file
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>IK Solver Interface</title>
    </head>
    <body>
      <h1>IK Solver Interface</h1>
      <form id="targetForm">
        <label for="x">X:</label>
        <input type="number" id="x" name="x" step="0.1" value="1"><br>
        <label for="y">Y:</label>
        <input type="number" id="y" name="y" step="0.1" value="1"><br>
        <label for="z">Z:</label>
        <input type="number" id="z" name="z" step="0.1" value="1"><br>
        <button type="submit">Send Target</button>
      </form>
      <script>
        document.getElementById('targetForm').addEventListener('submit', function(e){
          e.preventDefault();
          var data = {
            x: parseFloat(document.getElementById('x').value),
            y: parseFloat(document.getElementById('y').value),
            z: parseFloat(document.getElementById('z').value)
          };
          fetch('/send_target', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(response => response.json())
          .then(json => {
            console.log("Response: ", json);
            alert("Target sent: " + JSON.stringify(json.target));
          })
          .catch(error => console.error("Error:", error));
        });
      </script>
    </body>
    </html>
    """
    return html

@app.route('/send_target', methods=['POST'])
def send_target():
    data = request.get_json()
    x = float(data.get('x', 0))
    y = float(data.get('y', 0))
    z = float(data.get('z', 0))
    # Create and publish an LCM message with the target position
    msg = target_position.TargetPosition()
    msg.x = x
    msg.y = y
    msg.z = z
    lc.publish("TARGET_POSITION", msg.encode())
    print("Published LCM message with target: ", [x, y, z])
    return jsonify({"status": "sent", "target": [x, y, z]})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
