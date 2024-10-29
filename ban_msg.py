import random


def get_ban_msg(name: str, reason: str):
    if reason:
        return random.choice(
            [
                f"{name} took a one-way trip to Banland! Reason: {reason}",
                f"Oops! {name} just unlocked the 'Ban Hammered' achievement! Cause of celebration: {reason}",
                f'The Great Mod in the Sky has spoken. {name} has been "chosen" for removal due to: {reason}',
                f"{name} has vanished from the realm, mysteriously leaving only a note: *'I got banned for {reason}.'*",
                f"An unfortunate end befell {name}. Cause of demise: {reason}",
                f"The reckoning is here for {name}. Their offense: {reason}",
                f"{name} has been sacrificed to the Ban Gods. The offering? {reason}",
                f"A silence has fallen where once there was {name}. Reason for the silence: {reason}",
                f"The path to forgiveness was closed to {name}. Their transgression: {reason}",
                f"The decree was passed, and {name} paid the price. Their offense: {reason}",
            ]
        )
    else:
        return random.choice(
            [
                f"{name} took a one-way trip to Banland!",
                f"Oops! {name} just unlocked the 'Ban Hammered' achievement!",
                f"{name} has been sent to the Shadow Realm. We hope they enjoy their stay.",
                f'The Great Mod in the Sky has spoken. {name} has been "chosen" for removal.',
                f"Congrats, {name}! You've won a free, permanent vacation away from us. Enjoy it!",
                f"{name} has vanished from the realm, mysteriously leaving only a note: *'I got banned.'*",
                f'You could say {name} has... "logged off" forever.',
                f'Don"t worry about {name}; they"re just taking a "break."',
                f"{name} tried to cheat the system. The system won.",
                f'Good news: {name} doesn"t have to deal with us anymore! Bad news: we"re the ones who sent them away.',
                f"The Council has decided. {name} is no longer among us.",
                f"An unfortunate end befell {name}.",
                f"The reckoning is here for {name}.",
                f"{name} has been sacrificed to the Ban Gods.",
                f"A silence has fallen where once there was {name}.",
                f"They walked too close to the edge, and now {name} walks no more.",
                f"The path to forgiveness was closed to {name}.",
                f"Whispers of {name}'s name linger no longer.",
                f"The decree was passed, and {name} paid the price.",
                f"{name} gazed into the void... and the void banned back.",
            ]
        )
