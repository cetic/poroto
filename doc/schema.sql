CREATE TABLE `CompileInfo` (
            `id` INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT NULL,
        	`configurationName` VARCHAR(255) DEFAULT NULL,
            `timestamp` TIMESTAMP DEFAULT NULL,
            `compilerVersion` VARCHAR(255) DEFAULT NULL,
            `targetFlags` VARCHAR(255) DEFAULT NULL,
            `highFlags` MEDIUMTEXT DEFAULT NULL,
            `lowFlags` MEDIUMTEXT DEFAULT NULL,
            `pipeliningFlags` MEDIUMTEXT DEFAULT NULL,
            `streamFlags` MEDIUMTEXT DEFAULT NULL,
            `isCompiled` BOOL DEFAULT false          );
CREATE TABLE `ComponentInfo` (
            `componentName` VARCHAR(255) DEFAULT NULL,
            `id` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
            `type` VARCHAR(255) DEFAULT NULL,
            `area` INTEGER DEFAULT NULL,
            `frequency` INTEGER DEFAULT NULL,
	        `portOrder` MEDIUMTEXT DEFAULT NULL,
	        `structName` VARCHAR(255) DEFAULT NULL,
            `delay` INTEGER DEFAULT NULL,
            `active` BOOL DEFAULT false,
            `description` VARCHAR(255) DEFAULT NULL          );
CREATE TABLE `DatabaseVersion` (
			`version` VARCHAR(255) DEFAULT NULL);
CREATE TABLE `FileInfo` (
            `id` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
            `fileName` VARCHAR(255) DEFAULT NULL,
            `fileType` VARCHAR(255) DEFAULT NULL,
            `location` VARCHAR(255) DEFAULT NULL          );
CREATE TABLE 'Ports' (
	        `id` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
	        'readableName' VARCHAR(255) DEFAULT NULL ,
            'type' VARCHAR(255) DEFAULT NULL ,
            'portNum' INTEGER DEFAULT NULL ,
        	'vhdlName' VARCHAR(255) DEFAULT NULL ,
          	'direction' INTEGER DEFAULT NULL ,
        	'bitwidth' INTEGER DEFAULT NULL ,
          	'dataType' VARCHAR(255) DEFAULT NULL                      );
CREATE TABLE `ResourcesCalled` (
            `id` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
            `resourceID` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
            `resourceType` VARCHAR(255) DEFAULT NULL,
            `numUsed` INTEGER DEFAULT NULL          );
CREATE TABLE `ResourcesUsed` (
            `id` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
            `resourceID` INTEGER REFERENCES CompileInfo(id) ON UPDATE CASCADE ON DELETE CASCADE,
            `resourceType` VARCHAR(255) DEFAULT NULL,
	        `numUsed` INTEGER DEFAULT NULL          );
