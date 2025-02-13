import {
    Tabs,
    TabsHeader,
    TabsBody,
    Tab,
    TabPanel,
} from "@material-tailwind/react";
import { TabItem } from "../../utils/constants";

export interface TabsProps<T> {
    orientation?: "vertical" | "horizontal";
    value: string;
    tabItems: TabItem<T>[];
    data?: T;
    tabListClassName?: string;
    tabPanelsClassName?: string;
}

export function CustomTabs<T>({
    orientation,
    value,
    tabItems,
    data,
    tabListClassName,
    tabPanelsClassName,
}: Readonly<TabsProps<T>>) {
    return (
        <Tabs value={value} orientation={orientation}>
            <TabsHeader className={tabListClassName}>
                {tabItems?.map(({ id, label }) => (
                    <Tab
                        key={id}
                        value={label}
                        className={`text-text_primary font-semibold ${tabPanelsClassName}`}
                    >
                        {label}
                    </Tab>
                ))}
            </TabsHeader>
            <TabsBody>
                {tabItems.map(({ id, label, renderTabPanelComponent }) => (
                    <TabPanel key={id} value={label}>
                        {data ? (
                            renderTabPanelComponent(data)
                        ) : (
                            <p>Not found</p>
                        )}
                    </TabPanel>
                ))}
            </TabsBody>
        </Tabs>
    );
}
