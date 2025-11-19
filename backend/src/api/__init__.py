from flask_restful import Api as RestAPI

from api.healthcheck.resources import HealthyCheckResource
from api import reports


class API(RestAPI):

    def init_app(self, app):
        super().init_app(app)
        app.after_request(self.add_cors_headers)

    @staticmethod
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        return response


api = API()

# 世界地圖數據
api.add_resource(reports.WorldMapDataResource, '/world-map-data')
api.add_resource(reports.WorldMapExpenditureResource, '/world-map-expenditure')
api.add_resource(reports.WorldMapAvgSpendingResource, '/world-map-avg-spending')
api.add_resource(reports.WorldMapCrowdScoreResource, '/world-map-crowd-score')

# 國家詳細數據
api.add_resource(reports.JapanMonthlyVisitorsResource, '/country/JPN/monthly-visitors')
api.add_resource(reports.KoreaMonthlyVisitorsResource, '/country/KOR/monthly-visitors')
api.add_resource(
    reports.CountryExpenditureBreakdownResource,
    '/country/<string:country_code>/expenditure-breakdown'
)

# 健康檢查
api.add_resource(HealthyCheckResource, '/healthy')