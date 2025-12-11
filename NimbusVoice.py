import tkinter as tk
import sounddevice as sd
import speech_recognition as speechr
import json
import ollama
import NimbusVoice

def manual_parser(input):
    outJSON = {
        "sequence":  []
    }
    
    #{function name: Param 1, Param 2, etc 

    for i, word in enumerate(input.split()):
        try:
            word = word.lower()
            if word == "open":
                outJSON["sequence"].append({"open_app": input.split()[i+1]})
            if word == "close":
                outJSON["sequence"].append({"close_app": ""})
            if word == "click":
                #expect click to say comma as the separator
                outJSON["sequence"].append(    {"flat_select":    (input.split()[i+1], input.split()[i+3])}    )
            if word == "type":
                outJSON["sequence"].append({"keyboard_string": (input.split()[i+1], 70) }    )
            if word == "press":
                outJSON["sequence"].append({"KeyCom": (input.split()[i+1], "", "","") }    )
            
            
        except IndexError:
            print("Oops index error - mic prolly didn't catch full command")
            pass
    print(outJSON)
    return outJSON

AGENT_CONSTRAINT = r"""
You must follow the JSON schema and rules below EXACTLY.  
Return ONLY valid JSON, no explanations, no comments, no markdown.

CONSTRAINTS:
{
  "description": "Convert natural-language user intent into a sequence of allowed PC control function calls.",
  "output_format": {
    "type": "object",
    "required": ["Sequence"],
    "properties": {
      "Sequence": {
        "type": "array",
        "items": {
          "type": "object",
          "description": "One function call in the sequence. No additional text allowed."
        }
      }
    }
  },
  "rules": {
    "general": [
      "Read user input and interpret it directly as a series of intended PC actions.",
      "Interperet potential typos or ambiguous phrases.",
      "Return ONLY the JSON. No explanations. No surrounding text.",
      "If user instructions are ambiguous, assume reasonable defaults.",
      "If user instructions are impossible to interpret, return an empty Sequence array.",
      "Do not ask clarifying questions.",
      "Make sure to account for any actions provided after conjuctions like 'and' or 'then'.",
      "For mouse coordinates, assume the origin (0,0) is at the top-left of the screen.",
      "If the user says they want to 'click' at a location, use both the cursor_to_target and flat_select functions to accomplish their click task.",
      "Make sure the values in the parameters for cursor to target are integers."
      "Statements that relate to pressing keys should use the KeyCom function and be formatted as {'function_name': 'KeyCom', 'parameters': [Key 1, Key 2, ... where each key is either a modifier key (ctrl, shift, alt), a special key (tab, enter, esc, space, up, down, left, right, windows, backspace, delete, play/pause, volume up, volume down, volume mute, caps), a single character string representing a letter or number (a-z, 0-9), or a quick action (copy, paste, cut, select all, undo, new tab, close tab, control enter)."
    ],
    "functions_allowed": {
      "KeyCom": {
        "description": "Simulates pressing keys or predefined quick actions.",
        "parameters": [
          "Comm1",
          "Comm2 (optional)",
          "Comm3 (optional)",
          "Comm4 (optional)"
        ],
        "allowed_values": {
          "keys": [
            "ctrl", "shift", "alt", "tab", "enter", "esc", "space",
            "up", "down", "left", "right", "windows", "backspace",
            "delete", "play/pause", "volume up", "volume down", "volume mute", "caps"
          ],
          "letters": "Any single character string",
          "quick_actions": [
            "copy", "paste", "cut", "select all",
            "undo", "new tab", "close tab", "control enter"
          ]
        }
      },
      "keyboard_string": {
        "description": "Types raw text.",
        "parameters": ["text"]
      },
      "flat_hold": {"description": "Represents a hold that a user can also use to drag items.", "parameters": []},
      "flat_letgo": {"description": "Mouse release represents a release from the mouse button.", "parameters": []},
      "flat_select": {"description": "represent a mouse click.", "parameters": []},
      "open_app": {"description": "Opens an application on the PC.", "parameters": ["app"]}
      "close_app": {"description": "Close an application on the PC.", "parameters": ["app"]}
      "cursor_to_target": {"description": "Move the cursor to set of pixels on screen.", "parameters": ["x", "y"]}
    }
  },
  "behavior": [
    "The model must map user descriptions to the nearest appropriate function calls.",
    "The model must only use functions listed above.",
    "Every output must be a valid JSON object with the field 'Sequence' containing a list of function-call objects.",
    "Each item in Sequence must be exactly one function and its parameters.",
    "Once compiled, validate the JSON to ensure it adheres to the schema before returning.",
    "Then validate that all function names and parameters used are from the allowed functions list.",
    "Then validate that all parameter values are within the allowed values specified.",
    "Then validate that the overall sequence order matches the order in which the user asked the commands."

  ]
}
"""

def agent_parser(USERIN):
    prompt = f"""
    Return ONLY valid JSON with this exact structure:

    {{
    "people": string[],
    "locations": string[],
    "dates": string[]
    }}

    Fill the arrays based on the text.

    Text:
    {USERIN}
    """

    response = ollama.chat(
        model="llama3:8b",
        messages=[
            {"role": "system", "content": AGENT_CONSTRAINT},
            {"role": "user", "content": USERIN}
        ],
        options={"format": "json"}  
    )

    out = json.loads(response["message"]["content"])
    print(out)
    return out

def detect_wake_word(wake_word="nimbus", timeout=5):
    
    TransEngine = speechr.Recognizer()
    try:
        with speechr.Microphone() as source:
            print(f"Listening for wake word '{wake_word}'...")
            TransEngine.adjust_for_ambient_noise(source, duration=0.1)
            audio_data = TransEngine.listen(source, timeout=timeout)
        
        
        recognized_text = TransEngine.recognize_google(audio_data).lower()
        print(f"Heard: {recognized_text}")
        
        
        if wake_word.lower() in recognized_text:
            print("wake word retrieved")
            return True
        else:
        
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def run_sequence(INJSON):
    command_map = {
        "cursor_jump": NimbusVoice.py_cursor_jump,
        "cursor_smooth": NimbusVoice.py_cursor_smooth,
        "flat_hold": NimbusVoice.py_flat_hold,
        "flat_letgo": NimbusVoice.py_flat_letgo,
        "flat_select": NimbusVoice.py_flat_select,
        "cursor_to_target": NimbusVoice.py_cursor_to_target,
        "keyboard_string": NimbusVoice.py_keyboard_string,
        "KeyCom": NimbusVoice.py_KeyCom,
        "mouse_scroll": NimbusVoice.py_mouse_scroll,
        "open_app": NimbusVoice.py_open_app,
        "close_app": NimbusVoice.py_close_app,
    }

    for item in INJSON["sequence"]:
        print(item)
        print(item.keys())
        fn_name = list(item.keys() )[0]
        params = list(item.values())

        if fn_name in command_map:
            command_map[fn_name](*params)
        else:
            print(f"bad function name {fn_name} - parser probably made a mistake")

# test = {'sequence': [{'open_app': 'settings'}]}

# run_sequence(test)
def main_manual():
    def main_run():

        if not detect_wake_word(wake_word="nimbus", timeout=30):
            print("Wake word not detected. Try again.")
            # return
            main_run()
        
        
        USERIN = None
    
        TransEngine = speechr.Recognizer()
        with speechr.Microphone() as source:
            print("AUDIO ON - listening for command")
            TransEngine.adjust_for_ambient_noise(source, duration=.1)
            audio_data = TransEngine.listen(source, timeout=10)
            
            USERIN = TransEngine.recognize_google(audio_data)
            print(USERIN)
            OUTJSON = (manual_parser(USERIN))
            try:
                run_sequence(OUTJSON)
            except:
                print("error running sequence - likely a bad command from parser")

    while True:
        main_run()  
    
def main_agent():
    # First, wait for wake word
    if not detect_wake_word(wake_word="nimbus", timeout=5):
        print("Wake word not detected. Try again.")
        return
    
    USERIN = None
   
    TransEngine = speechr.Recognizer()
    with speechr.Microphone() as source:
        print("AUDIO ON - listening for command")
        TransEngine.adjust_for_ambient_noise(source, duration=.2)
        audio_data = TransEngine.listen(source, timeout=10)

    try:
        
        USERIN = TransEngine.recognize_google(audio_data)
        print(USERIN)
        

    except:
        USERIN = "ERROR"
        print("didn't pick up all audio")
        return

    if USERIN != "ERROR":
      OUTJSON = (agent_parser(USERIN))
      run_sequence(OUTJSON)
    
def sequence_activation(seq_json, backend):

    for item in seq_json["Sequence"]:
        fn = item["function_name"]
        params_list = item.get("parameters", [])

    
        params = {}
        for p in params_list:
            params.update(p)

        if fn == "KeyCom":
            c1 = params.get("Comm1", "")
            c2 = params.get("Comm2", "")
            c3 = params.get("Comm3", "")
            c4 = params.get("Comm4", "")
            backend.KeyCom(c1, c2, c3, c4)

        elif fn == "keyboard_string":
            text = params.get("text", "")
            typespeed = int(params.get("typespeed", 0))
            backend.keyboard_string(text, typespeed)

        elif fn == "flat_hold":
            backend.flat_hold()

        elif fn == "flat_letgo":
            backend.flat_letgo()

        elif fn == "flat_select":
            backend.flat_select()

        elif fn == "open_app":
            app = params.get("app", "")
            backend.open_app(app)

        else:
            print(f"[ISSUE] Unknown function_name: {fn}")

def ruler_overlay():
    import tkinter as tk
    SPACING = 50
    THICKNESS = 30
    LINE_COLOR = "#00ff00"
    TEXT_COLOR = "#00ff00"
    LINE_WIDTH = 1
    ALPHA = 0.5   # whole-window transparency (0.0 = invisible, 1.0 = opaque)


    def draw_vertical_ruler(canvas, height):
        for y in range(0, height, SPACING):
            # tick mark
            canvas.create_line(0, y, THICKNESS, y,
                            fill=LINE_COLOR, width=LINE_WIDTH)
            # number label
            canvas.create_text(THICKNESS // 2, y + 5,
                            text=str(y),
                            fill=TEXT_COLOR,
                            font=("Arial", 8))


    def draw_horizontal_ruler(canvas, width):
        for x in range(0, width, SPACING):
            # tick mark
            canvas.create_line(x, 0, x, THICKNESS,
                            fill=LINE_COLOR, width=LINE_WIDTH)
            # number label
            canvas.create_text(x + 10, THICKNESS // 2,
                            text=str(x),
                            fill=TEXT_COLOR,
                            font=("Arial", 8))


    def create_ruler(x, y, w, h, draw_fn):
        win = tk.Toplevel()
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", ALPHA)
        win.geometry(f"{w}x{h}+{x}+{y}")

        canvas = tk.Canvas(win, highlightthickness=0, bg="black")
        canvas.pack(fill="both", expand=True)

        draw_fn(canvas)
        return win


    def run():
        root = tk.Tk()
        root.withdraw()

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        # left vertical ruler
        v = create_ruler(
            0, 0,
            THICKNESS, screen_h,
            draw_fn=lambda c: draw_vertical_ruler(c, screen_h)
        )

        # top horizontal ruler
        h = create_ruler(
            0, 0,
            screen_w, THICKNESS,
            draw_fn=lambda c: draw_horizontal_ruler(c, screen_w)
        )

        # escape closes both
        root.bind_all("<Escape>", lambda e: (v.destroy(), h.destroy()))
        root.mainloop()

    run()

#little UI Interface
root = tk.Tk()
Title = tk.Text()

button1 = tk.Button(root, text = "Start Manual Parsing", command= main_manual, pady=5, padx=5, bd=0, highlightthickness=0)
button2 = tk.Button(root, text = "Start Agent Parsing", command= main_agent, pady=5, padx=5, bd=0, highlightthickness=0)
button3 = tk.Button(root, text = "Show Ruler Overlay", command= ruler_overlay, pady=5, padx=5, bd=0, highlightthickness=0)

button1.pack(pady=50)
button2.pack(pady=50)
button3.pack(pady=50)

root.title("Nimbus Voice Assistant")

root.geometry("500x500")
root.configure(background="#1f8948")

# ruler_overlay()
root.mainloop()

