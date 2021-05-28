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