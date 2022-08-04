Change log
==========

Version 1.0.1 (April 21, 2021)
-----------------------------------

* Publish project

Version 1.0.2 (April 23, 2021)
-----------------------------------

* Speed improvemetns

Version 1.0.3 (April 29, 2021)
-----------------------------------

* documentation improvements
* minor bug fix

Version 1.0.31 (April 29, 2021)
-----------------------------------

* readme fix for pypi

Version 1.1.0 (Mai 3, 2021)
-----------------------------------

* Add Tag Names to Commits
* Add Author and committer to Commits (the committer was the author before)
* Adapt documentation


Version 1.1.1 (Mai 19, 2021)
-----------------------------------

* Add get mutiple repositorys by whitelist and blacklist pattern


Version 1.1.2 (Mai 20, 2021)
-----------------------------------

* Fix get mutiple repositorys by whitelist and blacklist pattern

Version 1.1.3 (Mai 20, 2021)
-----------------------------------

* Fix extract_user_data.
* User name can cause an unknown Github exception 

Version 1.1.4 (Mai 20, 2021)
-----------------------------------

* enhance Fix extract_user_data.

Version 1.1.5 (Mai 27, 2021)
-----------------------------------

* add commits sha on pull_request
* solve author and committer problem
* add define_unknown_user to Version
* add get unknown_user from commits
* get_repos has now mutiple whitelist and blacklist pattern and are optional now


Version 1.1.6 (Mai 28, 2021)
-----------------------------------

* define unknown users takes now a dictionary in with unknown user as key and id as value. If the user is doesnt exists then a new user will be added.

Version 1.1.7 (Mai 28, 2021)
-----------------------------------

* Fix extract user. A name is sometimes not set!

Version 1.1.8 (July 15, 2021)
-----------------------------------

* Remove Example notebooks
* bugfix from type in version.py


Version 1.1.9 (July 28, 2021)
-----------------------------------

* bugfix in extracting user data from commit

Version 1.1.10 (July 28, 2021)
-----------------------------------

* hotfix for 1.1.9

Version 1.1.11 (July 29, 2021)
-----------------------------------

* change define unknown user in Utility!
* users can now be referenced with uuids from other users or a new user will be created

Version 1.1.12 (July 29, 2021)
-----------------------------------

* solved error: check for numpy is nan in Utility

Version 1.1.13 (July 29, 2021)
-----------------------------------

* solved error: ignore Alias if already there in Utility(define_unknown_user)

Version 1.1.14 (July 30, 2021)
-----------------------------------
* version download will check if there are defined user for unknown user
* comment out some print
* verion checks now if there are updates before downloading

Version 1.1.15 (July 30, 2021)
-----------------------------------
* define unknown user in Version works now only for one user
* if a anonym_uuid is known from a different repository for this unknown user then this anonym uuid will be extract_user_data
* The same unknown Author name will be connected to the same anonym_uuid

Version 1.1.17 (November 11, 2021)
-----------------------------------
* add output for crashed git pull operatins
* fix empty repositories

Version 1.1.18 (November 11, 2021)
-----------------------------------
* change README intructions
* Excrption handling for release count
* replace git pull by generation of a new clone


Version 2.0.0 (April 14, 2022)
-----------------------------------
* restructuring github2pandas
* easier to use
* main class github2pandas was added
* tests were reworked and extended
* github2pandas is now a lot faster!!!
* a good api call handling was implemented to save api calls

Version 2.0.1 (Mai 30, 2022)
-----------------------------------
* HotFix: removing complexity of git2net calculation


Version 2.0.2 (August 1, 2022)
-----------------------------------
* HotFix: fix wait for reset request limit