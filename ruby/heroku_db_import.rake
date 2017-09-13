require 'open3'

namespace :heroku do
  namespace :db do

    desc "Import the latest postgres DB snapshot from a Heroku application to the specified database"
    task :import, [:application, :target_environment] => :environment do |t, args|
      application = args[:application]
      target_environment = args[:target_environment]
      db_configuration = Rails.configuration.database_configuration[target_environment]

      capture_heroku_db_snapshot(application)
      backup_id = latest_backup_id(application)
      dump_path = download_backup(application, backup_id)
      restore_from_backup(db_configuration, dump_path)
    end

    private

    def capture_heroku_db_snapshot(application)
      shell "heroku pgbackups:capture --expire --app #{application}"
    end

    def latest_backup_id(application)
      shell "heroku pgbackups --app #{application} | cut -f 1 -d ' ' | tail -n 1 | tr -d '\n'"
    end

    def download_backup(application, backup_id)
      backup_url = shell %Q(heroku pgbackups:url #{backup_id} --app #{application} | tr -d '"\n')
      download(backup_url, filename: backup_id)
    end

    def download(url, opts={})
      path = opts[:path] || '/tmp'
      filename = opts[:filename] || '_downloaded.tmp'

      download_path = File.join(path, filename)
      if command_exists?('curl')
        download_with_curl(url, download_path)
      elsif command_exists?('wget')
        download_with_wget(url, download_path)
      end
      download_path
    end

    def download_with_curl(url, download_path)
      shell %Q(curl -o #{download_path} "#{url}")
    end

    def download_with_wget(url, download_path)
      shell %Q(wget -O #{download_path} "#{url}")
    end

    def restore_from_backup(db_configuration, backup_path)
      shell "pg_restore --verbose --clean --no-acl --no-owner -d #{db_configuration['database']} #{backup_path}", fail_on_error: false
    end

    def shell(command, opts={})
      failure_message = opts[:failure_message] || nil
      verbose = opts.has_key?(:verbose) ? opts[:verbose] : false
      fail_on_error = opts.has_key?(:fail_on_error) ? opts[:fail_on_error] : true

      puts "#{command}" if verbose
      output = `#{command}`
      puts "#{output}" if verbose
      exit_code = $?.exitstatus

      fail(failure_message || "'#{command}' failed with status (#{exit_code}) !") if fail_on_error && exit_code != 0

      output
    end

    COMMAND_NOT_FOUND_STATUS = 127

    def command_exists?(command)
      # Not using `which #{command}` since which is not guaranteed to behave consistently everywhere
      Open3.popen3(command)
      $?.exitstatus != COMMAND_NOT_FOUND_STATUS
    end
  end
end
