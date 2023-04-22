class Const:
    INSTANCE_CODE = 'viettelpost'
    DELIVERY_CARRIER_CODE = 'viettelpost'
    SERVICE_PRODUCT_CODE = 'ViettelPost'
    TYPE_SERVICE = 1
    TRACKING_LINK = 'https://viettelpost.vn/thong-tin-don-hang?peopleTracking=sender&orderNumber={bl_code}'
    PRODUCT_TYPE_CODE_HH = 'HH' # Hàng hóa
    NATIONAL_TYPE_CODE = '1'    # Bảng giá trong nước
    WAYBILL_TYPE_CODE_1 = '1'   # Không thu hộ
    WAYBILL_TYPE_CODE_2 = '2'   # Thu hộ tiền hàng và tiền cước
    WAYBILL_TYPE_CODE_3 = '3'   # Thu hộ tiền hàng
    WAYBILL_TYPE_CODE_4 = '4'   # Thu hộ tiền cước
    SERVICE_TYPE = 'LCOD'
    PRINT_WAYBILL_TYPE_1 = 1
    VTP_STATUS_TYPE_1 = 1   # Confirm order
    VTP_STATUS_TYPE_2 = 2   # Confirm return shipping
    VTP_STATUS_TYPE_3 = 3   # Delivery again
    VTP_STATUS_TYPE_4 = 4   # Cancel order
    VTP_STATUS_TYPE_5 = 5   # Get back order (re-order)
    VTP_STATUS_TYPE_11 = 11     # Delete canceled order
    VTP_PRINT_URL_A5 = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=1&bill={}&showPostage=1'
    VTP_PRINT_URL_A6 = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=2&bill={}&showPostage=1'
    VTP_PRINT_URL_A7 = 'https://digitalize.viettelpost.vn/DigitalizePrint/report.do?type=1001&bill={}&showPostage=1'
    VTP_PRINT_TYPE_A5 = 'a5'
    VTP_PRINT_TYPE_A6 = 'a6'
    VTP_PRINT_TYPE_A7 = 'a7'


class Message:
    BASE_MSG = 'Base Url ViettelPost not found.'
    MSG_ACTION_SUCCESS = 'Everything seems properly works well!'
    MSG_NOT_CARRIER = 'Delivery carrier ViettelPost not found.'
    NOTE_CONFIRM_ORDER = 'Xác nhận đơn hàng.'
    NOTE_CANCEL_ORDER = 'Hủy đơn hàng.'
    NOTE_WAITING_SHIPPER = 'Please wait for the staff to come pick up the goods.'


class FuncName:
    GetProvinces = 'GetProvinces'
    GetDistricts = 'GetDistricts'
    GetWards = 'GetWards'
    SignIn = 'SignIn'
    SignInOwner = 'SignInOwner'
    GetOffices = 'GetOffices'
    GetServices = 'GetServices'
    GetExtendServices = 'GetExtendServices'
    GetStores = 'GetStores'
    SetStore = 'SetStore'
    ComputeFeeAll = 'ComputeFeeAll'
    CreateWaybill = 'CreateWaybill'
    UpdateWaybill = 'UpdateWaybill'
    PrintWaybill = 'PrintWaybill'
    CheckShipCost = 'CheckShipCost'


class Method:
    Post = 'POST'
    Get = 'GET'
