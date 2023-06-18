import subprocess

def main():
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover', 'tests']
    )
