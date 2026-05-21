import environs

env = environs.Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN_ID = env.int("ADMIN_ID")

