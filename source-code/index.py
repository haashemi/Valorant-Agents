from PIL import Image, ImageDraw, ImageFont
import requests


class Utility:

    @staticmethod
    def get(api_url) -> dict:
        """
        Get URL with https request and returns Json encoded data
        """
        return requests.get(api_url).json()

    @staticmethod
    def get_image(image_url):
        """
        Get the URL and returns opened the image if response was 200, else NONE
        """
        res = requests.get(image_url, stream=True)
        return Image.open(res.raw) if res.status_code == 200 else None

    @staticmethod
    def font(size):
        return ImageFont.truetype("assets/font/Valorant.ttf", size)

    def fit_text(self, text: str, size: int, maxSize: int):
        """
        Make text smaller to fit that in specific width

        :param text: The text! nothing special
        :param size: Main font size
        :param maxSize: Max image width
        :return: New font size and other things
        """
        font = self.font(size)
        textWidth, _ = font.getsize(text)
        change = 0

        while textWidth >= maxSize:
            change += 1
            size -= 1
            font = self.font(size)
            textWidth, _ = font.getsize(text)

        return self.font(size), textWidth, change

    @staticmethod
    def align_center(foregroundWidth: int, backgroundWidth: int, distanceTop: int = 0):
        """
        Returns some number to align the image center

        :param foregroundWidth: Icon/Img width (px) wants to align it
        :param backgroundWidth: Background width that wants to paste something on it
        :param distanceTop: How may pixel want to move it up
        :return:
        """
        return int(backgroundWidth / 2) - int(foregroundWidth / 2), distanceTop


class Valorant:

    util = Utility()

    class Files:
        """
        File path of the assets
        """
        background = "assets/images/background.png"
        none_icon = "assets/images/icon.png"
        overlay = "assets/images/overlay.png"
        border = "assets/images/border.png"

    def agent_icon(self, data: dict):
        """
        Generates and save .PNG formatted image of the agent

        :param data: Dictionary type data of specific agent
        :return: Nothing (But saves an image in ./exports directory)
        """
        # Try to fetching specific things from data
        try:
            name = data["displayName"]
            char_url = data["bustPortrait"] if isinstance(
                data["bustPortrait"], str) else data["displayIcon"]
            abilities = data["abilities"]
        except Exception as error:
            return print(f"[ERROR OCCURED] {error}")

        # Open background image from assets as main image
        icon = Image.open(self.Files.background).convert("RGB")

        # Paste the borders on main image
        border = Image.open(self.Files.border)
        icon.paste(border, (0, 0), border)

        # Get and paste icon of agent
        char = self.util.get_image(char_url)
        if char is not None:
            char = char.resize((479, 479))
            icon.paste(char, (int((icon.width - char.width) / 2), 0), char)

        # Paste gradient overlay on all pasted things
        overlay = Image.open(self.Files.overlay)
        icon.paste(overlay, (0, 0), overlay)

        # Make an image to paste it on main content
        ability_img = Image.new(
            "RGBA", ((len(abilities) * 55) - 10, 40))

        # (For looping) inside of agent abilities list
        i = 0
        for ability in abilities:
            # Maybe some abilities doesn't have an image, so we can replace them
            # with Valorant-API.com logo
            if ability["displayIcon"] is None:
                ability_icon = Image.open(self.Files.none_icon)
            else:
                ability_icon = self.util.get_image(ability["displayIcon"])

            # Now resize them to 40x40px resolution then paste them on "ability_img"
            ability_icon = ability_icon.resize((40, 40))
            ability_img.paste(ability_icon, (i * 55, 0), ability_icon)
            i += 1

        # Paste the abilities image on the main image
        icon.paste(ability_img, self.util.align_center(
            ability_img.width, icon.width, 420), ability_img)

        # Draw final thing, it's name of the agent
        draw = ImageDraw.Draw(icon)
        font = self.util.font(56)
        textWidth, _ = font.getsize(name)
        change = 0
        if textWidth >= 260:
            font, textWidth, change = self.util.fit_text(name, 56, 260)
        draw.text(self.util.align_center(textWidth, icon.width, (int(
            360 + (change / 2)))), name, (255, 255, 255), font=font)

        # Save the image inside of ./exports directory with name of agent
        # as .PNG formatted image
        icon.save(f"exports/{name}.png")


if __name__ == "__main__":
    agents = Utility().get("https://valorant-api.com/v1/agents")

    for agent in agents["data"]:
        Valorant().agent_icon(agent)
