from sentry_sdk.integrations.flask import FlaskIntegration
import sentry_sdk


sentry_sdk.init(
    'https://4c732c2faeb959298cd894d8aae3b258@o4508444565831680.ingest.us.sentry.io/4508444763160576',
    integrations=[FlaskIntegration()],
)

