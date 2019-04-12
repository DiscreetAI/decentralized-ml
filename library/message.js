var __extends = (this && this.__extends) || (function () {
    var extendStatics = function (d, b) {
        extendStatics = Object.setPrototypeOf ||
            ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
            function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
        return extendStatics(d, b);
    };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var DMLMessage = /** @class */ (function () {
    function DMLMessage(id, repo, type) {
        this.id = id;
        this.repo = repo;
        this.type = type;
    }
    return DMLMessage;
}());
var DMLRequest = /** @class */ (function (_super) {
    __extends(DMLRequest, _super);
    function DMLRequest(id, repo, type, model) {
        var _this = _super.call(this, id, repo, type) || this;
        _this.repo = repo;
        _this.type = type;
        _this.model = model;
        return _this;
    }
    return DMLRequest;
}(DMLMessage));
