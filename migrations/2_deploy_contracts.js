const DataProvenance = artifacts.require("DataProvenance");

module.exports = function (deployer) {
  deployer.deploy(DataProvenance);
};