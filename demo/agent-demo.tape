# vhs tape: records the agent loop as an animated GIF for the README.
# Docs: https://github.com/charmbracelet/vhs
#
# Generate the GIF (from the repo root, with your .env filled in):
#     vhs demo/agent-demo.tape
# Output: demo/agent-demo.gif

Output demo/agent-demo.gif

Set Shell "bash"
Set FontSize 20
Set Width 1200
Set Height 640
Set Padding 24
Set Theme "Catppuccin Mocha"

# Show the command being typed, then run the finished demo agent.
Type "python demo/demo_agent.py"
Sleep 500ms
Enter

# Give the agent time to think, call its tools, and answer.
Sleep 8s
