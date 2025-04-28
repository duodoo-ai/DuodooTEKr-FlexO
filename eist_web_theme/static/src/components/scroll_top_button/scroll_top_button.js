/** @odoo-module **/

import {
    Component,
    onWillUpdateProps,
    useState,
} from "@odoo/owl";

export class ScrollTopButton extends Component {

    static template = "eist_web_theme.ScrollTopButton";
    static props = {
        target: { type: Object },
        show: { type: Boolean, optional: true },
        useParentEl: { type: Boolean, optional: true },
    };
    static defaultProps = { show: false, useParentEl: false };

    setup() {
        this.duration = 500;
        this.state = useState({
            show: this.props.show,
        });

        onWillUpdateProps((newProps) => {
            this.state = newProps;
            // console.log(this.state);
        });
    }

    onClickScrollToTop(ev) {
        ev.preventDefault();
        const self = this;
        let target = this.props.target.el;

        if (this.props.useParentEl) {
            target = target.parentNode;
        }
        try {
            $(target).animate(
                {
                    scrollTop: 0
                },
                self.duration
            );
        } catch {
            target.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        }


        return false;
    }
}

