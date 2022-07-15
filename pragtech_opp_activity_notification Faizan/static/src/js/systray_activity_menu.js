odoo.define('pragtech_opp_activity_notification.systray.ActivityMenu', function (require) {
"use strict";

var ActivityMenu = require('mail.systray.ActivityMenu');

ActivityMenu.include({
    events: _.extend({}, ActivityMenu.prototype.events, {
    	'click .o_mail_preview': '_onActivityFilterClick',
    }),

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onActivityFilterClick: function (event) {
        // fetch the data from the button otherwise fetch the ones from the parent (.o_mail_preview).
        var data = _.extend({}, $(event.currentTarget).data(), $(event.target).data());
        var context = {};
        if (data.filter === 'my') {
            context['search_default_activities_overdue'] = 1;
            context['search_default_activities_today'] = 1;
        } else {
        	console.log('INSIDEEEEEE ELSEEEEEEEEEEE');
            context['search_default_activities_' + data.filter] = 1;
        }
        this.do_action({
            type: 'ir.actions.act_window',
            name: data.model_name,
            res_model:  data.res_model,
            views: [[false, 'kanban'], [false, 'form']],
            search_view_id: [false],
//            domain: [['activity_user_id.active', '=', 'True']],
            context:context,
        });
    },
});
});
