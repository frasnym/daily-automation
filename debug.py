from dotenv import load_dotenv
from matchwatch.main import main as MWMain
from manutd.main import main as ManUtdMain


load_dotenv()

MWMain()
ManUtdMain()
