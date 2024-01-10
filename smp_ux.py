def autocomplete(ac_level, cmd, cmd_set, *args):
    if ac_level == 0:
        print("Autocomplete is disabled")
        return
    else:
        commands = [c for c in cmd_set if c.startswith(cmd)]
        if len(commands) == 1:
            cmd_set[commands[0]](*args)
        elif len(commands) == 0:
            print("Invalid command")
        else:
            if ac_level == 1:
                print(
                    "Ambiguous command, could be one of "
                    f"{', '.join(commands)}"
                )
            elif ac_level == 2:
                for idx, command in enumerate(commands, start=1):
                    print(f"    {idx}: {command}")
                option = input(
                    f"Select from the options above (1-{len(commands)}) or"
                    " leave blank to cancel: "
                )
                if not option:
                    return
                while option not in map(str, range(1, len(commands) + 1)):
                    option = input(
                        f"Please enter a number from 1-{len(commands)}: "
                    )
                cmd_set[commands[int(option) - 1]](*args)


def timestamp(num):
    mins, secs = divmod(num, 60)
    if mins > 60:
        hours, mins = divmod(mins, 60)
        return f"{hours}:{mins:02}:{secs:02}"
    return f"{mins}:{secs:02}"
