create_folder_name() {
	date +"%s"
}

delete_folder() {
	ssh robert@192.168.4.34 "rm -rf $folder_name"
}

get_diff_file_path() {
	# unused
	file_change=$(git status -s)
	IFS=$'\n'
	for status_path in $file_change;
	do
		file_path=${status_path:3};
	    echo "$file_path";
	done
}

init_folder() {
	ssh robert@192.168.4.34 "mkdir $folder_name"
	zip -r package.zip dqa-murano dqa-script
	scp -C package.zip robert@192.168.4.34:$folder_name/
	rm package.zip
	ssh robert@192.168.4.34 "unzip $folder_name/package.zip -d $folder_name/"
	ssh robert@192.168.4.34 "rm -rf $folder_name/package.zip"
}

run_exorobot() {
	log_name="$(create_folder_name).html"
	ssh robert@192.168.4.34 "sudo python $folder_name/dqa-script/exo-robot-runner run -I dqa-murano -i web -O -t="test_check_auth" -r 0"
	scp robert@192.168.4.34:$folder_name/report/dqa-murano/general_report/log.html $pwd_path/$log_name
	echo "$(pwd_path)/$(log_name)"
}

pwd_path=$(PWD)
folder_name="./robert/$(create_folder_name)"
init_folder
run_exorobot
delete_folder